"""HarfBuzz check of ss16, the Torchlette prose ligatures.

    python verify_ss16.py FONT [LEVELS_DIR]

FONT is a .ttf with glyph names. The cases are the ligature lab's tests for the 54
kept proposals (44 from the first lab, 10 from the second; cvNN and the glyph names are
the lab's ids and names). Checks:

1. every trigger fires under ss16 and, for ids up to 99, under its own cvNN alone;
   with ss16 off nothing it adds appears;
2. no negative case selects its own proposal's glyphs under ss16 (the lab checked
   each proposal alone; with all of ss16 on, a kept letter pair such as the ll in
   well-known may still fire inside a negative);
3. common English (the lab's word list, paragraph and course sentence) and common
   number strings are untouched by ss16 except where a kept proposal is meant to fire;
4. the spark line (ss15) wins over the spark bars (ss16) when both are on;
5. with LEVELS_DIR (web/levels), every line of lesson prose is shaped with ss16 on
   and off; each change must come from a kept proposal, and a summary is printed;
6. the dropped proposals 48 (word-final -ing) and 82 (the tensor logotype) are gone:
   no dropped glyphs or cv48; cv82 may belong only to the validated graphnodes circle
   contract, and the old word triggers still come out as plain letters;
7. ownership, from the font's GSUB alone: every glyph the ss16 lookups (and the lookups
   they call) can output belongs to a kept proposal or to a module's declaration, and
   every declared glyph exists and is output by ss16.

Proposals that font modules add to ss16 come from <PostScript name>.ss16.json beside
FONT (see modules/README.md); their glyphs count as kept proposals' glyphs.

Prose runs with the app's features (onum, pnum, ss01, ss02) unless a case says
otherwise. Prints failures and exits nonzero if there are any. With TS_WEB_SUBSET=1
(the web subset) the features web_features.txt leaves out (cvNN, ss15) are not checked.
"""
import collections, glob, json, os, re, sys, unicodedata
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from webfeatures import kept

FONT = sys.argv[1]
LEVELS = sys.argv[2] if len(sys.argv) > 2 else None
tt = TTFont(FONT); ORDER = tt.getGlyphOrder()
HBF = hb.Font(hb.Face(hb.Blob.from_file_path(FONT)))
PROSE = {'onum': True, 'pnum': True, 'ss01': True, 'ss02': True}
LINING = {'ss01': True, 'ss02': True}
DEFAULT = {}

def shape(text, feats):
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(HBF, b, feats)
    return [(ORDER[i.codepoint], p.x_advance, i.cluster) for i, p in zip(b.glyph_infos, b.glyph_positions)]
def names(run): return [g for g, _, _ in run]
def on(base, tag='ss16'): return dict(base, **{tag: True})

# The glyphs each kept proposal adds (NEW) and the existing glyphs it can also select (OLD).
D = 'zero one two three four five six seven eight nine'.split()
NEW = {1: ['f_b'], 2: ['f_h'], 3: ['f_k'], 4: ['f_j'], 5: ['f_t'], 6: ['f_f_t'], 7: ['t_f'], 9: ['f_y'], 16: ['t_w'],
       22: ['r_y'], 23: ['r_w'], 24: ['l_l'], 25: ['r.rn'], 26: ['c.cl'], 50: ['T_T.dlig'],
       81: ['T_o_r_c_h_l_e_t_t_e.ss11'], 84: ['n_e_t_w_o_r_k.ss11'], 85: ['g_r_a_d_i_e_n_t.ss11', 'g_r_a_d_i_e_n_t_s.ss11'],
       86: ['s_o_f_t_m_a_x.ss11'], 88: ['P_y_t_h_o_n.ss11'], 90: ['endash.range', 'hyphen.keep'], 91: ['minus.osf'],
       92: ['plusminus.osf'], 93: ['approxequal.osf'], 96: [c + s for c in 'stndrh' for s in ('.ord', '.ord.osf')], 97: [],
       98: ['slash.keep'], 99: ['colon.lf', 'colon.of'], 100: ['hyphen.case'], 102: ['arrowleft'], 103: ['arrowboth'],
       104: ['arrowdblright', 'arrowdblboth'], 105: ['uni27F6', 'uni27F5'], 111: ['at.op'], 114: ['multiply.osf'],
       115: ['multiply.case'], 116: ['space.tuple'], 117: ['percent.osf'], 118: ['space.unit'], 120: [],
       121: ['tag.v', 'tag.end', 'period.tag'] + [d + '.tag' for d in D],
       122: [f'spark.{k}' for k in range(10)] + ['spark.start', 'spark.sep', 'spark.end'],
       123: [f'sparkl.first.{k}' for k in range(10)] + [f'sparkl.{a}_{b}' for a in range(10) for b in range(10)] + ['sparkl.start', 'sparkl.sep', 'sparkl.end'],
       124: ['pbar.fill', 'pbar.empty', 'pbar.start.f', 'pbar.start.e', 'pbar.end.f', 'pbar.end.e'],
       125: ['t_p'], 137: ['x_t'], 145: ['f_u'], 148: ['r_v'], 166: ['b.backc'], 167: ['d.fwdb'], 169: ['t.out', 't_s.out'],
       171: ['v.vec'], 200: ['g_t.w200'], 207: ['d_u_a_l.arch']}
OLD = {91: ['minus'], 92: ['plusminus'], 93: ['approxequal'], 97: ['onehalf', 'onequarter', 'threequarters'],
       98: ['fraction'] + [d + s for d in D for s in ('.numr', '.dnom')], 120: ['uni2116']}
# Proposals that font modules add to ss16 (ctx.ss16_owner in modules/*.py): build.py writes
# them to <PostScript name>.ss16.json beside the font it builds; the web subset keeps the
# name, so a subset written to the same folder finds the same file.
SIDECAR = os.path.join(os.path.dirname(os.path.abspath(FONT)), f"{tt['name'].getDebugName(6)}.ss16.json")
BUILTIN = {g for v in list(NEW.values()) + list(OLD.values()) for g in v}
DECLARED = {}                                  # module glyph -> (proposal id, module)
SIDECAR_FAILS = []
if os.path.exists(SIDECAR):
    for k, v in json.load(open(SIDECAR)).items():
        if int(k) in NEW: sys.exit(f'{SIDECAR}: module {v["module"]} declares ss16 proposal {k}, which is build.py\'s')
        NEW[int(k)] = v['glyphs']
        print(f'ss16 proposal {k} from module {v["module"]}: {v["glyphs"]}')
        for g in v['glyphs']:
            if g in BUILTIN: SIDECAR_FAILS.append(f'{SIDECAR}: module {v["module"]} claims {g!r} for proposal {k}, but it is build.py\'s')
            elif g not in ORDER: SIDECAR_FAILS.append(f'{SIDECAR}: proposal {k} (module {v["module"]}) names {g!r}, which the font does not have (stale sidecar?)')
            DECLARED[g] = (int(k), v['module'])
ALLNEW = {g for v in NEW.values() for g in v}
OWNER = {g: i for i, v in list(NEW.items()) + list(OLD.items()) for g in v}
TAG = {123: 'ss15'}                              # the spark line is its own feature
missing = sorted(g for i, v in NEW.items() if kept(TAG.get(i, 'ss16')) for g in v if g not in ORDER)

# --- the lab's cases -------------------------------------------------------------
# (id, positives, expected glyphs (one positive at least must show each), negatives, lining positives, context)
G1 = [(1, 'fb', 'The offbeat result came from a halfbaked baseline.'), (2, 'fh', 'A halfhearted sweep of the learning rate wrecked the run.'),
      (3, 'fk', 'Stream the logs through Kafka before training.'), (4, 'fj', 'A fjord-shaped loss curve is a bad sign.'),
      (5, 'ft', 'Apply softmax after the last layer.'), (6, 'fft', 'The fft module turns a signal into frequencies.'),
      (7, 'tf', 'Split the portfolio returns into eightfold folds.'), (9, 'fy', 'Simplify the model until it stops overfitting.'),
      (16, 'tw', 'A network with two hidden layers is enough here.'), (22, 'ry', 'Store each query in a dictionary keyed by vocabulary.'),
      (23, 'rw', 'Run the forward pass, then the backward pass.'), (24, 'll', 'Recall that all small cells were filled.'),
      (25, 'rn', 'The kernel will learn to return the modern pattern.'), (26, 'cl', 'Each class in the cluster includes a clip.'),
      # the second lab's joins (ids over 99: ss16 only); sentences from the lessons
      (125, 'tp', 'Run the model on all 100 requests in batches of 10, and report the total number of output values produced.'),
      (137, 'xt', 'With a vocabulary, encoding turns text into ids, one per character, and decoding turns ids back into text.'),
      (145, 'fu', 'Training adjusts the three layers so that useful positions match and pass on useful information.'),
      (148, 'rv', 'Read the curve right-to-left: as you lower the threshold, precision can vary along the curve.')]
CASES = [(i, [trig, sample], NEW[i], [], [], DEFAULT) for i, trig, sample in G1]
# their words, under the app's features, and where they must not fire: across a word
# space, in capitals, and where a kept ligature takes the first letter (ftp's ft,
# diffuse's ff, impactful's tf)
CASES += [(125, ['output', 'outputs', 'outputting', 'footprint'], ['t_p'], ['ftp', 'Tp', 'TP', 'at peace', 'OUTPUT'], [], PROSE),
          (137, ['next', 'text', 'context', 'contexts', 'the next token'], ['x_t'], ['Xt', 'XT', 'TEXT', 'max t', 'x-t'], [], PROSE),
          (145, ['function', 'functions', 'full', 'useful'], ['f_u'], ['diffuse', 'diffusion', 'impactful', 'Fu', 'FULL', 'if u'], [], PROSE),
          (148, ['curve', 'curves', 'observe', 'server'], ['r_v'], ['Rv', 'CURVE', 'for v', 'r-v'], [], PROSE)]
# the second lab's word marks: whole words (a plural s allowed), never inside a
# longer word, never capitalised
CASES += [(171, ['vector', 'vectors', 'a vector of', '(vector)', 'one vector per document'], ['v.vec'],
           ['Vector', 'VECTOR', 'vectorize', 'vectorized', 'eigenvector', 'eigenvectors', 'vectorss', 'vector2', 'vec'], [], PROSE),
          (200, ['length', 'lengths', 'sequence length', 'fixed-length'], ['g_t.w200'],
           ['Length', 'lengthy', 'lengthen', 'wavelength', 'strength', 'lengthss', 'lengths2'], [], PROSE),
          (207, ['residual', 'residuals', 'the residual update', 'a residual.'], ['d_u_a_l.arch'],
           ['Residual', 'RESIDUAL', 'residually', 'residualize', 'dual', 'individual', 'residualss'], [], PROSE),
          (166, ['backward', 'backwards', 'the backward pass', '(backward)', 'call loss.backward first'], ['b.backc'],
           ['Backward', 'BACKWARD', 'backwardness', 'backwardss', 'back ward', 'backprop'], [], PROSE),
          (167, ['forward', 'the forward pass', 'forward.', 'forward-mode'], ['d.fwdb'],
           ['forwards', 'Forward', 'FORWARD', 'forwarded', 'forwarding', 'fastforward', 'ward'], [], PROSE),
          (169, ['output', 'outputs', 'the output shape', 'its outputs.', 'input and output'], ['t.out', 't_s.out'],
           ['Output', 'OUTPUT', 'outputting', 'outputted', 'throughput', 'input', 'inputs', 'putout', 'outputss'], [], PROSE)]
CASES += [(50, ['TT', 'SETTINGS', 'ATTENTION'], ['T_T.dlig'], ['Tt', 'T T'], [], DEFAULT),
          (81, ['Torchlette', '(Torchlette)'], NEW[81], ['Torchlettes2', 'torchlette'], [], DEFAULT),
          (84, ['network', 'networks', 'a neural network'], NEW[84], ['networking', 'subnetwork'], [], DEFAULT),
          (85, ['gradient', 'gradients.', 'the gradient', 'the gradients of'], NEW[85],
           ['gradientless', 'gradientsfoo', 'gradientss', 'subgradients', 'Gradients', 'Gradient'], [], DEFAULT),
          (86, ['softmax', 'softmax,', 'apply softmax'], NEW[86], ['softmaxed'], [], DEFAULT),
          (88, ['Python', 'in Python'], NEW[88], ['Pythonic', 'IPython', 'CPython'], [], DEFAULT)]
G3 = [
    (90, ['epochs 1-10', 'pages 34-36', 'from 2019-2025'], ['endash.range'],
     ['2025-10-31', '2025-10', '555-123-4567', 'BatchNorm-2d', 'a 10-fold split', 'x-1', '3.14'], []),
    (91, ['from -1 to 1', '(-0.5, 2)', 'x = -3'], ['minus.osf'], ['1e-3', 'BatchNorm-2', 'well-known', 'the -x flag', 'pre-2020', '2025-10'], ['from -1 to 1']),
    (92, ['0.5 +/- 0.1', 'error +-3%'], ['plusminus.osf'], ['a+-b', 'C++ code', '+ -', '+/x'], []),
    (93, ['about ~3 ms', 'so a ~= b'], ['approxequal.osf', 'approxequal'], ['~/data', '~user', 'x~3', 'a ~ 3', 'wave~'], []),
    (96, ['1st', 'the 22nd', '3rd', '11th', 'the nth', 'kth'], ['s.ord.osf', 't.ord.osf', 'n.ord.osf', 'd.ord.osf', 'r.ord.osf', 'h.ord.osf', 's.ord', 'h.ord'],
     ['month', 'with', 'tenth', 'Conv2d', '3D', '4thly', '1stride'], ['1st']),
    (97, ['keep 1/2 of', 'and 3/4.', 'a 1/4 split'], ['onehalf', 'threequarters', 'onequarter'],
     [(t, ['onehalf', 'onequarter', 'threequarters']) for t in ('11/2', '1/24', '1/2/2025', '2025/1/2', '1/2.5', '3/45')] + ['1/2/2025', '2025/1/2', '1/2.5'], []),
    (98, ['a 3/8 dropout', '7/16 of', 'step 10/3', 'F1 = 2/3'], ['fraction', 'three.numr', 'eight.dnom'],
     ['10/31/2026', '2025/10', 'CIFAR10/100', '1/1000', 'and/or', '3/8.5', 'a 0/1 label'], []),
    (99, ['12:30', 'a 3:2 split'], ['colon.of'], ['Note: 3', 'step 3: train', 'a:b'], ['12:30']),
    (100, ['U-Net', 'A-Z', 'GPT-4'], ['hyphen.case'], ['ReLU-like', 'BatchNorm-style', 'e-mail', 'T-shirt', 'X-ray'], []),
    (102, ['w <- w'], ['arrowleft'], [('x <-1', ['arrowleft']), 'a<b', 'a <= b'], []),
    (103, ['input <-> output'], ['arrowboth'], ['a < b', 'a -> b'], []),
    (104, ['A => B', 'A <=> B'], ['arrowdblright', 'arrowdblboth'], ['a >= b', 'a <= b', 'a == b', 'a = > b'], []),
    (105, ['train --> evaluate', 'b <-- a'], ['uni27F6', 'uni27F5'], ['a -- b', 'a - > b'], []),
    (111, ['y = A @ B'], ['at.op'], ['@property', 'user@host', 'A@B'], []),
    (114, ['28 × 28', '28x28', '3 − 1', '0.5 ± 0.1'], ['multiply.osf', 'minus.osf', 'plusminus.osf'], ['A × B', 'x × y'], []),
    (115, ['NxCxHxW', 'CxHxW', 'B×C×H×W'], ['multiply.case'], ['HxW', 'XxX', 'Box', 'aBxCxD'], []),
    (116, ['shape (1, 28, 28)', '[64, 10]', '(-1, 784)'], ['space.tuple'], ['(see 1, 2)', '1, 2, 3', '(a, b)', '(1,2)'], []),
    (117, ['98% accuracy', '5.5% error'], ['percent.osf'], ['100 % sure', 'a%', '%'], []),
    (118, ['10 ms', '44.1 kHz', '2 GB', 'took 3 s.'], ['space.unit'], ['5 seconds', '2 msgs', '3 sets', '3 m-long', '5 Volts', 'at 3 we'], []),
    (120, ['Exercise No. 5', 'No.12'], ['uni2116'], ['No. That is wrong', 'No.', 'Nope', 'UNo. 5'], []),
    (121, ['built on v1.2.3', 'v0.17', 'v12.1'], ['tag.v', 'tag.end', 'period.tag'], ['v2', 'vs. 2', 'dev1.2', 'v.2'], []),
    (122, ['loss {9,6,4,3,2,2,1}', '{1,5,3,8}'], ['spark.9', 'spark.start', 'spark.end'], ['{1}', '{a,b}', '{1, 2}'], []),
    (124, ['epoch 6 [======----]', '[==--]'], ['pbar.start.f', 'pbar.fill', 'pbar.empty', 'pbar.end.e'], ['a[-1]', '[=]', '[x]', '[-1]'], [])]
CASES += [(i, pos, exp, neg, lin, PROSE) for i, pos, exp, neg, lin in G3]

fails = []
def fail(msg): fails.append(msg)
checks = 0
for id_, pos, exp, neg, lining, base in CASES:
    seen = set(); cv = {f'cv{id_:02d}': True} if id_ <= 99 and kept(f'cv{id_:02d}') else None
    for text, ctx in [(t, base) for t in pos] + [(t, LINING) for t in lining]:
        off, onr = shape(text, ctx), shape(text, on(ctx))
        seen |= set(names(onr)); checks += 1
        if off == onr: fail(f'{id_}: {text!r} does not change under ss16: {names(onr)}')
        if ALLNEW & set(names(off)): fail(f'{id_}: {text!r} with ss16 off shows {sorted(ALLNEW & set(names(off)))}')
        if cv:
            cvr = shape(text, dict(ctx, **cv))
            if cvr == off: fail(f'{id_}: {text!r} does not change under cv{id_:02d} alone')
            stray = {OWNER.get(g) for g in names(cvr) if g in ALLNEW} - {id_}
            if stray: fail(f'{id_}: cv{id_:02d} alone selects glyphs of {sorted(stray)} in {text!r}: {names(cvr)}')
    miss = [e for e in exp if e not in seen]
    if miss: fail(f'{id_}: expected glyphs {miss} never appear')
    for t in neg:
        # a negative must not select this proposal's glyphs (other kept proposals may
        # still fire inside it: a ll in well-known, a true minus in [-1])
        t, forbid = (t, None) if isinstance(t, str) else t
        off, onr = shape(t, base), shape(t, on(base)); checks += 1
        new_here = set(names(onr)) - set(names(off))
        own = {g for g in new_here if OWNER.get(g) == id_} | (set(forbid or []) & set(names(onr)))
        if own: fail(f'{id_}: negative {t!r} selects {sorted(own)}: {names(onr)}')

# 169 with 125: output keeps the tp join and ends in the arrow; the plural runs it over the s
for text, want in (('output', ['o', 'u', 't_p', 'u', 't.out']), ('outputs', ['o', 'u', 't_p', 'u', 't_s.out']),
                   ('outputting', ['o', 'u', 't_p', 'u', 't_t', 'i', 'n', 'g']), ('input', ['i', 'n', 'p', 'u', 't'])):
    g = names(shape(text, on(PROSE))); checks += 1
    if g != want: fail(f'169/125: {text!r} gives {g}, not {want}')
# the word marks replace exactly their own letters
for text, want in (('vector', ['v.vec', 'e', 'c', 't', 'o', 'r']), ('vectors', ['v.vec', 'e', 'c', 't', 'o', 'r', 's']),
                   ('length', ['l', 'e', 'n', 'g_t.w200', 'h']), ('lengths', ['l', 'e', 'n', 'g_t.w200', 'h', 's']),
                   ('residual', ['r', 'e', 's', 'i', 'd_u_a_l.arch']), ('residuals', ['r', 'e', 's', 'i', 'd_u_a_l.arch', 's']),
                   ('backward', ['b.backc', 'a', 'c', 'k', 'w', 'a', 'r', 'd']), ('backwards', ['b.backc', 'a', 'c', 'k', 'w', 'a', 'r', 'd', 's']),
                   ('forward', ['f', 'o', 'r_w', 'a', 'r', 'd.fwdb']), ('forwards', ['f', 'o', 'r_w', 'a', 'r', 'd', 's'])):
    g = names(shape(text, on(PROSE))); checks += 1
    if g != want: fail(f'word mark: {text!r} gives {g}, not {want}')
# 85: the plural takes its own logotype (not the singular's and a plain s), alone or in ss16
for text, want in (('gradients', ['g_r_a_d_i_e_n_t_s.ss11']), ('gradients.', ['g_r_a_d_i_e_n_t_s.ss11', 'period']),
                   ('(gradients)', ['parenleft', 'g_r_a_d_i_e_n_t_s.ss11', 'parenright']), ('gradient', ['g_r_a_d_i_e_n_t.ss11']),
                   ("gradients'", ['g_r_a_d_i_e_n_t_s.ss11', 'quotesingle'])):
    for base in (DEFAULT, PROSE):
        for feats in ({'ss16': True}, {'cv85': True}):
            if not kept(*feats): continue
            g = names(shape(text, dict(base, **feats))); checks += 1
            if g != want: fail(f'85: {text!r} under {sorted(feats)} gives {g}, not {want}')
for text in ('gradientsfoo', 'gradientss', 'xgradients', 'Gradients', 'gradients2'):
    g = names(shape(text, on(PROSE))); checks += 1
    if {'g_r_a_d_i_e_n_t.ss11', 'g_r_a_d_i_e_n_t_s.ss11'} & set(g): fail(f'85: {text!r} picks up a gradient logotype: {g}')
# ss15: the spark line replaces the bars when it is on, alone or with ss16
for feats, want in (({'ss15': True}, 'sparkl.end'), ({'ss15': True, 'ss16': True}, 'sparkl.end'), ({'ss16': True}, 'spark.end')):
    if not kept(*feats): continue
    g = names(shape('loss {9,6,4,3,2,2,1}', dict(PROSE, **feats))); checks += 1
    if want not in g or (want == 'sparkl.end' and 'spark.end' in g): fail(f'spark {feats}: {g}')
g = names(shape('{9,6,4}', PROSE))
if ALLNEW & set(g): fail('spark glyphs with ss15 and ss16 off')

# common English and numbers: unchanged with ss16 on, apart from the kept triggers
COMMON = ('the of and to a in is it you that he was for on are with as his they be at one have this from or had by hot word but what '
          'some we can out other were all there when up use your how said an each she which do their time if will way about many then them '
          'write would like so these her long make thing see him two has look more day could go come did number sound no most people my over '
          'know water than call first who may down side been now find any new work part take get place made live where after back little only '
          'round man year came show every good me give our under name very through just form sentence great think say help low line differ '
          'turn cause much mean before move right boy old too same tell does set three want air well also play small end put home read hand '
          'port large spell add even land here must big high such follow act why ask men change went light kind off need house picture try us '
          'again animal point mother world near build self earth father head stand own page should country found answer school grow study '
          'still learn plant cover food sun four between state keep eye never last let thought city tree cross farm hard start might story saw '
          'far sea draw left late run while press close night real life few north open seem together next white children begin got walk example '
          'ease paper group always music those both mark often letter until mile river car feet care second book carry took science eat room '
          'friend began idea fish mountain stop once base hear horse cut sure watch color face wood main enough plain girl usual young ready').split()
TRIG = ['fb', 'fh', 'fk', 'fj', 'ft', 'tf', 'fy', 'tw', 'ry', 'rw', 'll', 'rn', 'cl', 'TT', 'tp', 'xt', 'fu', 'rv']
words = COMMON + [w.capitalize() for w in COMMON[:50]]
for w in words:
    fires = any(t in w for t in TRIG)
    a, b = shape(w, DEFAULT), shape(w, on(DEFAULT)); checks += 1
    if not fires and a != b: fail(f'common word {w!r} changes under ss16: {names(b)}')
    if fires and a == b: fail(f'common word {w!r} has a trigger but does not change')
ENGLISH = ('The quick brown fox jumps over the lazy dog. When we train a model, we first look at the data and then choose a loss. '
           'It is often easier to start with a small net and grow it later. Each lesson in this course asks you to write a little code, '
           'run it, and read what comes back. A good habit is to print the shape of every array you make; most bugs show up there first. '
           'Mary and William went to New York on a Wednesday in March, and Anna met them at the station with a map. We would rather be slow '
           'and right than fast and wrong. Numbers such as 3.14 and 2,048 should look the same as before. Notice how the slope points uphill, '
           'so we step the other way. This sentence mentions torches, tensorflow, networking and Pythonic code, none of which should change. '
           'Whatever happens next, the model only learns what the data can teach it.')
G1_IDS = {i for i, *_ in G1}
g = names(shape(ENGLISH, on(PROSE))); checks += 1
unexpected = sorted({x for x in g if x in ALLNEW and OWNER[x] not in G1_IDS})      # only letter-pair ligatures may fire here
if unexpected: fail(f'English paragraph: unexpected {unexpected}')
for w in ('torches', 'tensorflow', 'Pythonic'):
    if ALLNEW & set(names(shape(w, on(PROSE)))): fail(f'{w!r} picks up a logotype')
COURSE = ('In PyTorch, a tensor flows through a neural network; the gradient of the loss after softmax tells each epoch how to move. '
          'NumPy and Python came first, torch.nn came later, and Torchlette runs it all in the browser. Torches, tensorflow and networking stay plain.')
got = sorted({x for x in names(shape(COURSE, on(DEFAULT))) if x.count('_') >= 3}); checks += 1
exp = sorted(['n_e_t_w_o_r_k.ss11', 'g_r_a_d_i_e_n_t.ss11', 's_o_f_t_m_a_x.ss11', 'P_y_t_h_o_n.ss11', 'T_o_r_c_h_l_e_t_t_e.ss11'])
if got != exp: fail(f'course sentence logotypes {got} != {exp}')
NUMS = ['2025-10-31', '3.14', 'v2', 'The quick brown fox jumps over the lazy dog.', 'In 2019, 60,000 images.', 'Train for 10 epochs; then evaluate.',
        'x - y', 'well-being', 'state-of-the-art', 'It costs $5.', 'pages 3, 4 and 5', 'Section 2.1', 'version 3', 'at 9 am', 'top-5 error',
        'float32', 'MNIST-like', 'A/B testing', 'and/or', 'see (a) and (b)', 'months', 'ninth', 'with', 'Mr. Smith', 'No, thanks.']
for t in NUMS:
    a, b = shape(t, PROSE), shape(t, on(PROSE)); checks += 1
    if {OWNER[x] for x in names(b) if x in ALLNEW} - G1_IDS: fail(f'number string {t!r} changes: {names(b)}')

# the feature's name
gsub = tt['GSUB'].table
rec = [r for r in gsub.FeatureList.FeatureRecord if r.FeatureTag == 'ss16']
if not rec or rec[0].Feature.FeatureParams is None or tt['name'].getDebugName(rec[0].Feature.FeatureParams.UINameID) != 'Torchlette prose ligatures':
    fail('ss16 has no feature name "Torchlette prose ligatures"')
def graphnodes_cv82_problem():
    """Allow cv82 reuse only for the built font's existing graphnodes contract.

    This is ownership/routing validation, not a graphnodes outline-quality test.
    The normal graphnodes verifier independently checks its geometry.
    """
    circles = {0x25CB: 'latent.graphnodes', 0x25C9: 'observed.graphnodes', 0x25CF: 'filled.graphnodes'}
    cmap = tt.getBestCmap()
    records = [r for r in gsub.FeatureList.FeatureRecord if r.FeatureTag == 'cv82']
    if len(records) != 1:
        return 'expected exactly one cv82 feature'
    if not all(cp in cmap for cp in circles) or len({cmap[cp] for cp in circles}) != 3:
        return 'three distinct default circles are not encoded'
    feature = records[0].Feature
    params = feature.FeatureParams
    if params is None or sorted(getattr(params, 'Character', [])) != sorted(circles):
        return 'cvParameters must own exactly ○ ◉ ●'
    if tt['name'].getDebugName(params.FeatUILabelNameID) != 'Inline graphical-model nodes':
        return 'cvParameters UI label is not graphnodes'
    mapping = {}
    for index in feature.LookupListIndex:
        lookup = gsub.LookupList.Lookup[index]
        if lookup.LookupType != 1 or lookup.LookupFlag != 0:
            return 'cv82 must contain only plain single substitutions'
        for subtable in lookup.SubTable:
            if set(mapping) & set(subtable.mapping):
                return 'duplicate cv82 source mapping'
            mapping.update(subtable.mapping)
    if mapping != {cmap[cp]: target for cp, target in circles.items()}:
        return 'cv82 mapping is not exactly the three graphnodes alternatives'
    classes = getattr(tt['GDEF'].table, 'GlyphClassDef', None) if 'GDEF' in tt else None
    classes = classes.classDefs if classes is not None else {}
    for cp, target in circles.items():
        if target not in ORDER or target in cmap.values() or classes.get(target) != 1:
            return f'{target}: expected an unencoded GDEF base glyph'
        for base in (DEFAULT, PROSE):
            text = 'x' + chr(cp) + 'z'
            default = shape(text, base)
            off = shape(text, dict(base, cv82=False))
            enabled = shape(text, dict(base, cv82=True))
            if off != default or len(off) != 3 or off[1][0] != cmap[cp]:
                return f'U+{cp:04X}: feature-off/default circle or positions changed'
            if len(enabled) != 3 or enabled[1][0] != target or any(g == ORDER[0] for g, _, _ in enabled):
                return f'U+{cp:04X}: cv82 does not select its declared graphnodes glyph'
    return None


cvs = sorted(r.FeatureTag for r in gsub.FeatureList.FeatureRecord if r.FeatureTag.startswith('cv'))
GRAPHNODES_CV82 = False
if 'cv82' in cvs:
    problem = graphnodes_cv82_problem()
    GRAPHNODES_CV82 = problem is None and kept('cv82')
    checks += 1
    if problem is not None:
        fail(f'cv82 ownership: {problem}')
    if not kept('cv82'):
        fail('cv82 is present despite the web feature policy omitting it')
want_cv = sorted({f'cv{i:02d}' for i in NEW if i <= 99 and kept(f'cv{i:02d}')} |
                 ({'cv82'} if GRAPHNODES_CV82 else set()))
if sorted(set(cvs)) != want_cv: fail(f'cv features {sorted(set(cvs))} != {want_cv}')
if missing: fail(f'glyphs missing: {missing}')

# ownership, read from the font rather than the corpus: every glyph the ss16 lookups can
# output (single, multiple, alternate, ligature and reverse-chain outputs, and those of the
# lookups that contextual and chaining rules call, at any depth) must belong to one of
# build.py's proposals or to a module's declaration in the sidecar
RESTORED = {'hyphen', 'slash'}                 # S16_KEEP_RESTORE puts the plain glyphs back
def ss16_outputs(tag='ss16'):
    table = tt['GSUB'].table; lookups = table.LookupList.Lookup
    todo = [i for r in table.FeatureList.FeatureRecord if r.FeatureTag == tag for i in r.Feature.LookupListIndex]
    seen, out = set(), set()
    def nested(o, acc):
        if type(o).__name__ in ('SubstLookupRecord', 'LookupRecord'): acc.append(o.LookupListIndex)
        elif isinstance(o, list):
            for x in o: nested(x, acc)
        elif hasattr(o, '__dict__') and type(o).__module__.endswith('otTables'):
            for x in vars(o).values(): nested(x, acc)
    while todo:
        i = todo.pop()
        if i in seen: continue
        seen.add(i); lk = lookups[i]
        for st in lk.SubTable:
            t = lk.LookupType
            if t == 7: st = st.ExtSubTable; t = st.LookupType
            if t == 1: out |= set(st.mapping.values())
            elif t == 2: out |= {x for seq in st.mapping.values() for x in seq}
            elif t == 3: out |= {x for alts in st.alternates.values() for x in alts}
            elif t == 4: out |= {l.LigGlyph for ls in st.ligatures.values() for l in ls}
            elif t == 8: out |= set(st.Substitute)
            elif t in (5, 6): nested(st, todo)
    return out
OUTPUTS = ss16_outputs()
for m in SIDECAR_FAILS: fail(m)
unowned = sorted(OUTPUTS - BUILTIN - set(DECLARED) - RESTORED)
if unowned:
    why = (f'not declared in {SIDECAR}' if os.path.exists(SIDECAR) else
           f'and there is no {SIDECAR}: a module that adds to ss16 must declare its glyphs with ctx.ss16_owner')
    fail(f'ss16 can output {unowned}, which no proposal owns ({why})')
for g, (k, mod) in sorted(DECLARED.items()):
    if g in ORDER and g not in OUTPUTS: fail(f'{SIDECAR}: proposal {k} (module {mod}) declares {g!r}, which no ss16 lookup outputs (stale sidecar?)')
checks += 1

# the dropped proposals: 48 (word-final -ing) and 82 (the tensor logotype)
DROPPED = {48: 'i_n_g', 82: 't_e_n_s_o_r.ss11'}
for i, g in DROPPED.items():
    if g in ORDER: fail(f'dropped {i}: glyph {g} is still in the font')
    if f'cv{i:02d}' in cvs and not (i == 82 and GRAPHNODES_CV82):
        fail(f'dropped {i}: cv{i:02d} has no validated replacement owner')
cmap = tt.getBestCmap()
for w in ('training', 'Training', 'trainings', 'sampling', 'running', 'embeddings', 'thing', 'tensor', 'tensors',
          'Tensor', 'tensor-valued', 'a tensor of tensors', 'training tensors'):
    plain = [cmap[ord(ch)] for ch in w]
    for base in (DEFAULT, PROSE):
        for feats in ({'ss16': True}, {'cv48': True, 'cv82': True}):
            if not kept(*feats): continue
            a, b = shape(w, base), shape(w, dict(base, **feats)); checks += 1
            if a != b: fail(f'dropped: {w!r} changes under {sorted(feats)}: {names(b)}')
    if names(shape(w, on(DEFAULT))) != plain: fail(f'dropped: {w!r} is not plain letters under ss16: {names(shape(w, on(DEFAULT)))}')

# lesson prose: every change must come from a kept proposal
if LEVELS and os.path.isdir(LEVELS):
    hits = collections.defaultdict(collections.Counter); nlines = 0
    for path in sorted(glob.glob(os.path.join(LEVELS, '**', '*.md'), recursive=True)):
        t = unicodedata.normalize('NFC', open(path, encoding='utf-8').read())
        t = re.sub(r'^---\n.*?\n---\n', '', t, count=1, flags=re.S)
        t = re.sub(r'^(```|~~~)[^\n]*\n.*?^\1[ \t]*$', '\n', t, flags=re.S | re.M)
        t = re.sub(r'<(script|style|svg|pre|code)\b.*?</\1>', ' ', t, flags=re.S | re.I)
        t = re.sub(r'(`+)(.+?)\1', ' ', t, flags=re.S)
        t = re.sub(r'\$\$.+?\$\$', ' ', t, flags=re.S); t = re.sub(r'\\\[.+?\\\]|\\\(.+?\\\)', ' ', t, flags=re.S)
        t = re.sub(r'(?<![\\$])\$(?!\s)([^$\n]+?)(?<!\s)\$(?!\d)', ' ', t)
        t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t); t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'https?://\S+', ' ', t)
        for line in t.split('\n'):
            if not line.strip(): continue
            nlines += 1
            a, b = shape(line, PROSE), shape(line, on(PROSE))
            if any(g in ALLNEW for g in names(a)): fail(f'{path}: ss16 glyph with ss16 off')
            if any(g in ('hyphen.keep', 'slash.keep') for g in names(b)): fail(f'{path}: a protected hyphen or slash is left in {line[:60]!r}')
            if a == b: continue
            ca, cb = collections.defaultdict(list), collections.defaultdict(list)
            for g, _, c in a: ca[c].append(g)
            for g, _, c in b: cb[c].append(g)
            bl = line.encode('utf-8')
            for c in sorted(set(ca) | set(cb)):
                if ca.get(c) == cb.get(c): continue
                if c not in cb: continue                       # taken into a ligature that starts earlier
                owners = {OWNER[g] for g in cb[c] if g in OWNER}
                ctx = bl[max(0, c - 8): c + 12].decode('utf-8', 'replace')
                if not owners: fail(f'{os.path.relpath(path, LEVELS)}: change with no ss16 glyph at {ctx!r}: {ca.get(c)} -> {cb[c]}')
                for o in owners: hits[o][ctx] += 1
    print(f'lesson prose: {nlines} lines shaped; changes per proposal:')
    for o in sorted(hits, key=str):
        print(f'  {o}: {sum(hits[o].values())}' + ('  e.g. ' + ', '.join(repr(k) for k, _ in hits[o].most_common(3)) if hits[o] else ''))
print(f'{FONT}: {checks} ss16 checks, {len(fails)} failures')
for f in fails: print('FAIL', f)
sys.exit(1 if fails else 0)
