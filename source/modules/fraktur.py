"""fraktur: Mathematical Fraktur capitals 𝔄..ℨ and lowercase 𝔞..𝔷 (SC4).

Covers all 52 characters of Unicode's Mathematical Fraktur alphabet:
- the five BMP Letterlike Symbols capitals ℭ ℌ ℑ ℜ ℨ (U+212D, U+210C, U+2111, U+211C, U+2128),
- the 21 SMP Mathematical Alphanumeric Symbols capitals 𝔄 𝔅 𝔇 𝔈 𝔉 𝔊 𝔍 𝔎 𝔏 𝔐 𝔑 𝔒 𝔓 𝔔 𝔖 𝔗 𝔘 𝔙 𝔚 𝔛 𝔜
  (U+1D504..U+1D51C less the five reserved holes), and
- the 26 SMP Mathematical Alphanumeric Symbols lowercase letters 𝔞..𝔷 (U+1D51E..U+1D537),
used for Lie algebras (𝔤, 𝔰𝔬(3), 𝔰𝔲(2), 𝔰𝔩_n(ℝ)), prime and maximal ideals (𝔭 ⊂ 𝔪), real and
imaginary parts (ℜ, ℑ), and Turing's 1936 m-configurations (𝔟, 𝔠, 𝔮, 𝔭, 𝔣).

Source and attribution. Reference outlines are adapted and topology-cleaned from Noto Sans Math
(Copyright 2022 The Noto Project Authors, https://github.com/notofonts/math, SIL Open Font
License 1.1, no Reserved Font Name; google/fonts ofl/notosansmath/NotoSansMath-Regular.ttf,
version 3.000), the same OFL sans math reference used by `mathletters` and `ui`. Fraktur capital 𝔙 (U+1D519) is redrawn with an open top (approved Q-FRAK-OPEN), cleanly distinguishing it from 𝔅 (U+1D505) across all sizes including 18 px. The cleaned
52-glyph quadratic master and precomputed ray-clearance table are embedded in `_MASTER_B85`
so builds need no external binary font file. Nothing is named after Noto Sans Math.

Proportions and metrics. Capitals scale vertically by 705 / 714 to Torchlette's 705-unit cap
height (split-stem crests ~717, 𝔇 flourish 744, descenders of 𝔉 ℌ 𝔍 𝔓 𝔜 ℨ at -198). Lowercase
bodies up to y = 500 scale by 484 / 493 to match Torchlette's XH = 470 (diamond peaks at 484,
descenders at -193), while ascenders above y = 500 stretch to 732 on 𝔟 𝔡 𝔣 𝔥 𝔨 𝔩 (pairing with
Torchlette's 750 ascenders); the diamond tittles of 𝔦 and 𝔧 scale uniformly around their mapped
centres. Sidebearings open by FRAK_SB (default 1.22) so Fraktur letters breathe inside roman and
italic math prose.

Weight progression and topology invariance. The fraktur darkens across the family as the Latin text
around it does: a style whose Latin stems are SV times Regular's (Light 0.758 through Black 2.470)
gets fraktur stems of about 67 * SV units (the master's are 67, the Latin Regular's 66), so its ink
relative to Regular follows the Latin's (see the weight model above `_modulate_and_polish`). Bold
styles widen the letters (sx = 1 + 0.22 (SV - 1)) and move every point along the mitred offset of
its edges by the rest of the stem growth, hairlines by a fraction of it (𝔰's diagonal hairline,
which runs between its two small counters, not at all); a point takes at most 0.30 of its exterior
clearance, and a counter under 70 units keeps what it can, so split stems, double bars and small
counters (𝔊 ℌ ℑ ℜ 𝔚 ℨ 𝔞 𝔤 𝔥 𝔨 𝔰 𝔷) stay open through Black; edges never turn back, so contours cannot
loop; the top and bottom fifths of the glyph take the vertical growth back, so the baseline,
x-height, cap height, ascenders and descenders stay where Regular has them. Light narrows a little
and thins every stroke but the hairlines. Integer rounding is followed by a point-count-preserving
tangent polish (a polish move that would make a sliver loop is undone), keeping identical contour
counts, point counts and on-curve flags across all 14 styles with zero `outline_check` defects or
contour overlaps. Regular is the master, unchanged.

Italics. Mathematical Fraktur is semantically upright (like double-struck ℝ in `symbols` or UI
icons in `ui`), including inside italic theorem prose. In italic styles `glyphs` places a
counter-sheared outline so `build.py`'s reslant restores it upright, and `post` (running before
`meta`'s `ttfautohint`) writes the exact upright integer-polished outline so upright and italic
weights share identical outlines without double-shear rounding jitter.

Cmap and subsetting. Before mapping SMP code points, `glyphs` ensures `(3, 10)` and `(0, 4)`
format 12 Unicode cmap subtables exist and preserve every existing BMP mapping, composing cleanly
when `mathletters` runs after `fraktur`. Glyph names: `uni212D`, `uni210C`, `uni2111`, `uni211C`,
`uni2128`, and `u1D504`..`u1D537`. All 52 glyphs get GDEF class 1 and participate in no `smcp`
or `c2sc` substitutions. Code points outside the Makefile's `UNICODES` web subset: the 47 SMP
code points `U+1D504..U+1D537` (the five BMP capitals in `U+2100-214F` stay in the web subset).
Knobs (environment): `FRAK_SB` (default 1.22), `FRAK_BOLD` (default 1.0).
"""
from array import array
import base64
import copy
import math
import struct
import zlib

import pathops
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

FRAKTUR_CHARS = (
    (0x1D504, '𝔄', 'A'), (0x1D505, '𝔅', 'B'), (0x212D, 'ℭ', 'C'), (0x1D507, '𝔇', 'D'),
    (0x1D508, '𝔈', 'E'), (0x1D509, '𝔉', 'F'), (0x1D50A, '𝔊', 'G'), (0x210C, 'ℌ', 'H'),
    (0x2111, 'ℑ', 'I'), (0x1D50D, '𝔍', 'J'), (0x1D50E, '𝔎', 'K'), (0x1D50F, '𝔏', 'L'),
    (0x1D510, '𝔐', 'M'), (0x1D511, '𝔑', 'N'), (0x1D512, '𝔒', 'O'), (0x1D513, '𝔓', 'P'),
    (0x1D514, '𝔔', 'Q'), (0x211C, 'ℜ', 'R'), (0x1D516, '𝔖', 'S'), (0x1D517, '𝔗', 'T'),
    (0x1D518, '𝔘', 'U'), (0x1D519, '𝔙', 'V'), (0x1D51A, '𝔚', 'W'), (0x1D51B, '𝔛', 'X'),
    (0x1D51C, '𝔜', 'Y'), (0x2128, 'ℨ', 'Z'),
    (0x1D51E, '𝔞', 'a'), (0x1D51F, '𝔟', 'b'), (0x1D520, '𝔠', 'c'), (0x1D521, '𝔡', 'd'),
    (0x1D522, '𝔢', 'e'), (0x1D523, '𝔣', 'f'), (0x1D524, '𝔤', 'g'), (0x1D525, '𝔥', 'h'),
    (0x1D526, '𝔦', 'i'), (0x1D527, '𝔧', 'j'), (0x1D528, '𝔨', 'k'), (0x1D529, '𝔩', 'l'),
    (0x1D52A, '𝔪', 'm'), (0x1D52B, '𝔫', 'n'), (0x1D52C, '𝔬', 'o'), (0x1D52D, '𝔭', 'p'),
    (0x1D52E, '𝔮', 'q'), (0x1D52F, '𝔯', 'r'), (0x1D530, '𝔰', 's'), (0x1D531, '𝔱', 't'),
    (0x1D532, '𝔲', 'u'), (0x1D533, '𝔳', 'v'), (0x1D534, '𝔴', 'w'), (0x1D535, '𝔵', 'x'),
    (0x1D536, '𝔶', 'y'), (0x1D537, '𝔷', 'z'),
)

_MASTER_B85 = (
    'c-ri|SDX}O@HYCsJ>8RfLeF%bnav4y*(L0fm$W(WY!2ioSp+0!5d@J8B1t5pxPS-'
    '}1Qbz0L=Z^|B7!2KfC3VRbgE|0ck%z7@8X<`bFR)+{c5ITRXtTty`fVGdzO+;G={_wT1qaP|9egYTCREa3mV'
    'YRn41zB2)}Nsr6f>2*tnD-fyy)NX#)x5j5fT@l0ZZ#2paILWKdJTrKO;0GiU+_;=1XHk-VyGx6iVX{f)NU6&'
    'L+CW4nExL;^*#tqV00=yKGwP@{peY9ne{cMK+#1RBp`%Hfc(S<G8*xb!UMkrOVxfZJgMG2R?&qpxVq%~d?jR'
    'iCgYc(OtpPVo?ZIPD<PfNwZGE|Wl1AHzPK1lsO5KJ=16$r<xQFAdZvJZfF1I#$AeohJ(2WK!mzD8P*hb0-'
    'QPIY^gw|L}XvWRs_zsmw?Zg#2c0XQ0PwkMrXgvaacT+gOIK3`@6<VaR*B&DqyLw<!NQFB-'
    '^)N;7vZNA{|(i@8R6xaf5;NugE6uZv!d^wJ{4?K)j5oe}@iX+WMNT~TSIf1C7NBd*pq<*J7S5?z|rM*_aKy4'
    '6PmA#L?ycwFUeMTGwvzpZ>O(?HSNN=G9N6u+$`a3sB$RUd;NdaVONv*Xh>(6YR}^-'
    'C=MMY*k`AJj?O0q|H<wjvP{NSY#}Z<P~LQ}C_&pS0-'
    '(St0)?{r!S&@cbt=CFEi39%&RfJjWw7pycn$d1AJKGy#F$e97-'
    '_&yoZ+#|iHam$omVG~nIEe*~9K?qR8ZK>{8QLMe?VkOX4LCwHA8aG(6&9U<^n*$ev@pp~z(TjBV!fB9w*Q6='
    'A5FrrH5n81L6;uYL3h@s|25HygWvZzI#WY!qSeDx&rJwyA+Cz+uP>8peq;O0k^K}-X92JJq51Q%28Q#d3b-'
    '>3cHJiRNs%t($TR2zRW(mAQ`o17*xsdTC}(M(>}ZrV&%@@mo|dpb`iwqN3ivy-'
    '=qmN<TM(u3to933U{sPZSP83LsIsL2ct%j{)Dt*xEi0O1+8ifIY)<ypn7g=kY(F_&C$_cHdH1I&_aB6iU3nX'
    'lUDeEmc73!V<p78^5c<Sk{WVF(<e)zQ;%f?7xafYU+iq>w<!7Q?S_hbFuU!!tA5g27s}$&Ol0Ct-'
    'z31AQ}GF@O=ZtJnsPRQpQ@;mN#Xl`kPc`b^d^YBZ}p7|zosYXr{I-'
    '`3W7XdwB5wh>OK4%b8Agwm;c54cM4T+bf3ZGqjZDR856ULD>jF~g@rnCYuPknM6<NH@^rX(78Mh??Q5%|&;G'
    'UG{VqNJ-_oP#=J?W?iVq0s*-'
    '$G}lN1>7BeEfgd8qtFJ%|DU0Qk7!p6a(ETkP<fQANgZ`MhPQ2|TEuzYlG8b80)<V7GqN|ip9e}&v*Hc?3k%2'
    '{dYD<NzEK-!iDw$PfkxyuJR(LDvghuwO8-&9OUDoTC>ySv^sk-I*U7#&NFaq&b$mG0q4Q?HBOt}U@rd-tDh3'
    'E>~;9bj+K&uVj*G)8#wZXf>0wMRVz7JlYT2ZEgOES)iQynxA`LP={b(1U9LGP3mx!@ho7M*b(wvhXsW;q_3>'
    'H6kZ?eooKQX<3mH<5<gar0Iq4GsOt`ZGroOK;lxvGnEA$Bx?!IaGSujSrEO7(qxnKq7`P9Y}Mh2q36ccoA&U'
    '{VDqhp09HqZEPh0e;o~T(m-'
    'w<b%<cgEr#>pre@hD0!bm{h=qWA)o>m)<yHG+4{4!Zu&0AV!~KpUI*~)|&P|v_ik)}B=dCU~XF~+!4-'
    'oK#!fgVcUi3Vu6_>aN!+%8+#EWobQ4eV_oL9V9{tJSn&2KU$s0L#d)bvK`DmX;>R*eIpo{}*Pt6q^K00jQi('
    'p`w0l7-'
    'SQ5Jx5dxVNd~c=0t?YmM%M8*S4_U6CLFYCdec+X)!j+vtu1G347|UkF#x{^i#phW_O*OZ2noe|e}0JCpKkb4'
    '9YNbe6ruMSd(j>o9;pN}f6&fTv1)uDxKTl2NXp`$oB1LEwRQ+zhXBUsz`%v)Wy9b~n-'
    'ijZ2+}I8xQ{h+Sn#Ojw=m5kqT+G;=_viL1TgT*}bgnujjX2IYP#FEx<&!uqT4VY2)a6KOze=*|EiRj+n61s_'
    '%G0=lY3C*#=f1v)Kj9Qy`Ob`(aMKVZqG+SmBb2KsBaZ*50eG9`>S)*8u<27Mf#o5=Q*J`RtWe$cj$qs~m~a&'
    'OwBtz=(GjC~SM50_Z1j|Donbg;$YCR56yEvMaNR7tc&6X{5Qv}Kt{#$?A^FG}?FW=pJ4q2@&9*+!_Ozt-CRh'
    'DJx~=WO8e-3r5pc*$7#f+fUD$18J8puHI~jy)@racxYHi8F$km`Nsc+#YzPoDT#Q-'
    'lg<{okG^E*lsxuuUn>>uS2@*aME}kY!E+!L(RLzFbDpVni*91QSN2zXd)*Ynk*enbbr=%5ahjrOly>hZYjH9'
    'Uk)DdT(I8+f3&(_ue6dy#sAtWZRCUUfB7%%^kn&O)+{HTR$;bI709THBuj*wOsz_?eBh?bLHj`@Tk>Ax@5*F'
    'w>~7~omBgxJ+=o><F!FDEoQI^BZ?r)4jn9~40&QN)uIxySY>8ULOpr;PwuqT4(hrqI4CIs*vd_5ML5C?PxRZ'
    'AJv0g`OffFco^cZI8IywU4)RW7uf@n`TYvw}$WQTY@ga!(Kcc51Jg@kpu+X4M799ccp`wY(WCxq^VtE44_La'
    '7KeO$dcR3q)S_)B<p|6Y4(5Hep{#nBh`FNL%?$Fl<r_^-V~F;p04Wps1;%e3v0NhK%x^HPb-MDBmIo=9VVS0'
    'Y#=_ooG_&<t|6v&)|-7zA#@Q$J7V*&t<a8*Ug4BsbLQrJpOm>dfEh$yj||KKX%bKD-'
    '2FZ6@QjTxbE`s+);oG8mNqM&9ackovzw1n`mK3KYkfdg;?Fz!bs$bSM6PZF;q5mTxMza$~%rymQ1Ql6vn~>R'
    '_qX>z}MvuU4D2c|5FhkzKt2eCo`C}=nyi<UdGY($_q;wM_OnfngM$Go`sf~7W$DMVtr~N>$N95+-'
    'IdS$lk(8H!21vXy@dag2zmjX)}fH7P`zcQ<!8W>!M~kqwHi?$-'
    '9mk2i;ThGjDJM9$r`*isZx68fy!QEGVzBj+f{h(7ut#n<b~LkSXS7b>YhuIy3nL9_rSF*gD%ym6X@xVTAm@!'
    'Na(EJj|}g!`wDO_-+UIKC_UA#Z#?-|JGfD*}z|)4f@n)gH```vO#?s?_8h8yVa-hF8?Eq=lwrT<K8Sx<C0#V'
    '#vA53|Av&CaweF@v+C1$Zhachk97r;`e*KLQ0oiFixOt@mC_D4FR!V*1I}ymlZ={YtTG!8kt5YO5b9#N2T<+'
    'W68Q$?@AC7~0+n<wUI>ELl%xeU{~9;2)x|}VT`M#?qcBluqLcBR<~p0`bWH5`4$xL=#1W&>J@D|5koKrCc5u'
    'ggAu;v}h0cnJu?q?r-'
    '(;u#Pl>!%y2Y_fq>D@T3SSHK^XeV0w_LPPUhgh+laY<*iNi$lW}~yBL!$kfEtEiXO%df>uvzPHrM;U3I<`<R'
    'xoDtS3pE@>+#@+#Ac2>9%Q9GZ$VLf7+qP-'
    'a0ViqGysJ1zAWcjAxEU91s<d&*0!^vRcCU7j<|UD$2z;#EC7!lHkY9Jl0{n{Ka_{Bo#RAzK%ae1-'
    'J6ti~xUl7}9+1Mk)h<YHbHEP}?74~saF9hq5eI#UW?S|M?0DX?>=6Jv-B=L-'
    '8^^Qh&qyF9o<*{o6wi)=qMx#yi#L$r(0a57yd_^W!L_=?T{OL9q?Mr;O^GH_qyK0GD%w*qgP=9aE*7*}nPGu'
    'XbXA)gIG`$edseWJV{nLIp=*^|6KDg}XiJod^z=nrKH%u+sAvm7d2PZ{(-uH&+wI07gnrj5-'
    'T31Rawg>*x9B;!m2i%G@eDG-Iquu1@RmbOpTkpYZLF_9hIe3XuRn%28tp*Mv&uCP4oO_)dI4=h`&F(_3HdMg'
    'mNSnfpH+-@L>lSBim^Q8`L0#Xt<!kYr~Iio6!=onQ*$#X?UDP`d`BQtTK&U+B9mdBM~-'
    'xjZtI`SU(iY4tTOWjoo;HioCED(LoZXOkRNp~(@~<|s9pxj{Z~o_XA@`-'
    'mE+)IYdnqU*Whop5q$~Br`Cur$L#&Cp$UX_^hHw^0HD<<YZkyE&E`a{bd7ilVALg6hMp==c})fe5{L~`wn51'
    'ImMW-8<?1Z#zJ5{f!;kV_=`7IO(K96^B7HPzzD&1uyDZL-$(n8#-'
    '4Mu|yJouwDYUNZe%E1z9PHd*0E~>P`oRg!+m(vf_&kYh^1jBWxahp5ukoo)GOTF3eX@;y+&N#!bdaIVe6F4F'
    'Dm{Kg@ovo=B$pqRjF2*sYL1Y4*=ZoOOvHAf%^dfuJU!iOzY9c%>TiWjHqzGrgL9LOCWmzaK@zk~#|fUc>*90'
    'en@Mq{?7j@?y+RfH0ky5jm*!yZ&X*oSJ<83OCO;>E_Nneqz|(PWIxt#2RtV(m`p&EqF$x&0$_G3auE>_$?{I'
    'd09R;2n=vGI2!}C?u(S88Jq7LjEn7=+TV<QssHjizI?h3Xgs^2jRw6LwtCEx}zQILFew0OgL%}e6l!<;o<;+'
    '8r%tzP<8lbJ#<@S8l?wNa<(+7;n1jSkj~0wlba@=iyQhZcrOj-EP6ij*ASuvSTu1E_yaVZL*sOjlM<6gr4xe'
    'eFa6ieGI72!X_AKE?u46{ZVdctNgqZE?~B@5k;ifs{8qCBN??yOgcUK{x$WUatNjl0Dio^#)MQsHN&xGCADo'
    'm@-'
    '45i}O}W3pKi`$Rvg6q|9%Us&txDVv?X?%BkKc!IO=z>a2vq`^kSOJ201iptSYUf$}Kjdw8Q}YqYN*l=9xy&p'
    '}Eps`b1M)HZyXX8>sK%buB_2`#-I5Yk%DdWc|OtsVu@)^xpQgs=|1r~U&*R^L-'
    'zc9AeyQSJzE`bO<5C;7B`gm)hl_nHyjAkiJ+g^C);T&W?>6UK|^IMq#RtVe8gow|!ZVk0NKui9%I<o(1~?Wd'
    'e{Y09hi_Aav7UtrrU(%sbxpRbU&suUjDr;!y3581nCQG^X%yIJEx`(O{Xhp)1K>7gk}hi%Y2s_Gv+@zRFc>t'
    '@g@L!Pql$Ye$Pr|eLHo+xpc;eOi`k&F-?Kp@FS-4Eb-'
    '<j%@Z@N|)bv<L{w)`PSbki@bFY2A^qf1u##P0d*mvT~qR7$j#1ohdHVycGgGcR=3lyakXD-'
    '*q$vNF?dD6Y&1t%~lBez4|{U(DF4ScgsP)9ejeDXCjkp4)J)~NE>umIWz`Bo6aD$Cg8E%5~cv1B_o>-'
    'W1$rYv>Rm@3usBV8omJ|HrdF0W2AqER)HWVv}Y8Fk~W;;(|Y@{_bhaK?QZs&nY^9Q##nA5(^@;sWkxbQ<_ri'
    'r(!19J+Fs?h^%D~r8*$q@!%T-'
    'Xxou6dkkOq&tfGyqC?l3J4!XH?jS2i3C>d;w1SaPnYy?&lC?0Hl0$S$FCa9Q!Cf7~(AS@yaEMH)2zu7tpqAJ'
    'qP|Ajr=+dLNk?B%v#^Y*tLwW9YO4IvDRhdHtBFOCvsfoQn^1PwH-cA=*G-J5af=(;-'
    'uMXEc)Lw2cV7Z4GD;}HU6<*aN@fPl@+pYB|tlA?kX5VWlLjsvu={tI^C08@)y_DLF@Q2YT8RsWTC*&yhs7#n'
    'IULPlBPV(V3-'
    'wXH^1E3GUZl`Mofg*TcI)5`LTOeQqlXn9j2bNt2D1d;aeD?Akcx~`G7E^d;h_Xc7>Mnq&gfnj%vn<%_4k+SB'
    'uT#$!zn^3n=p_!xpK@o_1=zbUAlJKF}2~u^<Kna?~KvjFSH_(LI6i+ckO;w5~7MOWSiU<1gKyGX8ec-gsS4i'
    '!k3`aF^e+l8~nd?Lj2mQqT=Om}YS=*}Tq+`SRwn5Kn$A%y9tDe&_Esyd4Jtu|QF~02!>W@CgUwuIa7Jq78Ov'
    'v1ZzgiX(x;T8i8MKw^L*u^Z<W=pVao{sL9mFqB$XnWFvoS!XtHoAhfKE{Q@}Rw<G`2@SA@8Uw?P*VGJAJC--'
    'V^$|mpIl#R#uPkkyw9=t&vcFm6yyx?KwB|3DoB299$X&4yozm%}Xfh;%Q<vFtj@6wl$d{wMp}#sU@8w&)WJL'
    'Xm#j5yUjp%g)Fpx&5(Zj+xBS;ogA^!-'
    'jE@m6xTSA&u1E(p_KmDyrobB6++E&uO{S*r<cqa$m2$l>K{h(utTH@H2r>Fq}s+t?v#mgi9pWP+;Y9<Ci_Y|'
    '39q^7zD7At(Dp|kw?TTHuD`~=FVI63<u<_N_|j7Q_cn5%Y@dCbm0U00XD_hQTZJGj<bGy<TQ?Kg)u5O42aeP'
    '#&9URGj&uQRbA!XqOcUZa9ROaZf5tY%s(+6rh(UpFSMJd?$ftS=iz8%VOHEK&0?k@kRzq~B{bkt?TE<_NW`L'
    '2XudFD#9I>8*9}EBBo5CR_@lHtUfs%5e4j@)|&2=A#@ci!kkd;F|cB7`x69*#vT1jr5HVeBUx^-'
    'enctu>PleSG>!6Do7<X6PO9%$-4(gT24(o7J5UQtG^*=D&2MDk|&2;3-'
    'fv+RTCjE$DIsidRIyC*6nB1RX06vbq2b$%k#MgTa_+WQ~cs}yprq_O>5g<dXUc$Y@c`z7ltjr>^J!JMv>6D_'
    'k$&>S31bQ?kYGTP2I*2ves3ru%~+*dC!V4fe83(Rzp991hgU|%Po>scc}^P5GEn{kx40UI31@6DR0LKqbKjL'
    '_l)V(+p`p|=T*XHoNQXQ2I=p`|mup?g(_(|1AWf6|u?L8D({q400uE<sNe={BMk{iE?9h=$3g58%f}b4)n$-'
    '#Eei8i=;9fS`elr$H@ck_FF;jkCg!N4tht<5{}e``GdaLyi<QvhkE0jg}ldrC<A;0%*T@`nVMX`8KkT`z@A!'
    'meR+~a%5jS*&S&lpO*Pt&`ut&YAl?v(390)J9^;&-'
    'gbMIlWeHiZoloM@0D)19}vjK+yjoc++=Cv0YXQK#OqbA;}VTfmb!u3h3oGC!=nwudPtzPjT<FHj~Qq(O4cB='
    'B#x4|Lfkd_Pl^E1Yy}9qCh@WeTHi)%#DgMjmDp8$Ng|~YkKMpaCwo#skk!g^0Z#~7E}VAJ9!-'
    '}Eon53)>U}{L$k>X9t{<VCRo`<zgfvxsS9C$IQT3N}*95#RL&kzsnjv?E66DX2$3d~mzAHlS5J-'
    '^Sso*hRn(HVa*6S2PA)$Hi*>FrXVzBijIJMP43u@_hpmuq|`UgOgO+bWh=+jvlfwYHeVo)R^koM3djP}Qd?+'
    '{3}rc4CVQ#1C6Y1=HD5lGuCNOq!TTTyg*!+IEj1UwOebjN{>YKbnaKp<^$T|pqp?kfnSF>ciKGO-eY^i+JV0'
    'gyff0YGXl&O#tH7cU@?nv2y4q{|`>wj>ouR}o0(gF`RP2Fq;_NQ33=2&BO>4j9JX5LY0OPPzstBrN7<CzOe('
    '%wZsCLcwDPXsQ1F_H+c&J=-1x(pT2!Dgfz%WflU7H8(*Z@unsSq;p&o1k(2gF9K;LlaD}J$s{6>Rx-'
    'm7NIG{Bf#f&M5$H#H8ZlZvgd82;0a82-'
    'bnjq32RS;&ZEOM@J8n1I1X`s~VgPNKn$AF`4=BUwL=gI9W(s)6+nt*NzKU`iQH#B0ECLPswK&k4CYa+uYyXK'
    'EwT`VUcqEh?`0>Z;^Oo<P)2-e^mIu$si5!OS@s#|~=ANzl6Y@hysH6K6dP&m-'
    '&;rUB_rPc5hlnw5AoX9g7~_WK?^rtT{*;oRD&BPc&d{sXv98kwa=F$ijE8vZe9<uxC|S(~dl4Y0vax-'
    '(gS=PK*v>oYin7Lb$iU0<iycs@KWM58EhN&=V{&~i(Qqgm6J!#m=ZX_#8W$!=ptX*RlRrZQ#mNptP@KFL5wt'
    '<VxNBAbf*wemCxSMxkzd>;(w2#Kv8zN%BHnj*mFObREf;8~)RqD=;qaD1duaAswiMby^k(f98bF1wXyUQ}FR'
    'UCd;`n{%!SYYgtyB$`aq6dJu>3ceF8dp?H8kOIgIv*AKsyP?!By%KM?SW?o2~hvrEIXEmg@kp<ky4c6|$YdJ'
    '}BJ8YyuIM&a?%LMWiz)0dckIm=yzUhtt;}RYsT?=;Q<8E15fh&FImFJMd%aXDn(B2XJq*^s?7yj9}^X&~4cI'
    'PmbHh4Q1%~&f7RYB~#k-CPK(kJ=aVK-KmuDpv?#?;pZ6W>^3EQ7mm!$_|0;}LcS@@HD}l$7c4SDQ4N$Y;wFM'
    '2D(AA0&jK}bS%(PxXD*AgqlL4K*k&aDWkJk%Qyn;as4W+89!Ndv4r*^HI1CihTgUPi{lqf^CwZQDIPg^CC!S'
    'q!&4iu$E;p2kOc3Pf)CU?X(oWG<05Ylah3cF{dNdBz%O%<eghwHx8=h7GL8C$+1G^+WwDkg{hJk9a1GLF%rn'
    'QYurg@K=S}J5%<D;fmB-%aWs0r$mzxrqM92ZTg7-'
    '*RzkhrpNezl!A{pGfeJgw2=dC1<O@}JgA0*R6SumV|3lz+3rBV}lfY>>o9d5az0WHQ6I%=wE<UyDr?;8`ZM$'
    'iT+@)#i&_tyJ1Oxz-'
    'J$Yfn|YA(N36BPHni#ubQi2aygfDpBsZNZ$q@DA!#yGyDTZfiSCnB<}?4wthzpbCNasH5YNvyOBrT`|TvUtU'
    '#P?qra427F$CXQeu`lGep~J`6a+l$!kgk6gU4R<z<M1;`u6%bC{Dfo}qzgNe6Ac=XV`QSU~OP`3)y1^HiXff'
    'iBk-EXk$uN+`r^rA5w!a4T;m0Z@<nABY_o`jLO0Xfu$N{sZm+OD2`{asSKFS4-'
    'Nsk}R}GNxTqgBQ^dMXS9tD_APP5+JJJNwS8fwHPsjFiDuHh=z@JMM~7uzun%R(s@Auy*d~T_HDi>kADe<r;}'
    'm0C5Wf3dPYnGt><-'
    'YH*+J02kUj>~;sxTh`)qWdZ;X4YljdlV;w>jx<cSnJLq?2?5SI#MQzyUsl8a0z^tm8Z78U>OghIF|p&tmkG<'
    '>H6v=!cGHt_r!&mlg+P2N@y@qJx%u6&3OcagdBIexJ~7D#{aaLq-M6Hr-D-'
    '@^4KOC0#TWy5XwytV7ij}eZS+3#_X^|9dxuxrx=hBKgrG&A@aI$!q&5i1X;&A`}7YX%2H)Kmj9koGeS4LKSZ'
    '`Mm+CXJ9~k_7!kox3wVXmTq@ZTh#3e2lQfa*CHbrduEs8<|ru5+Htc9`tB4EP_OeI8m}VRILFlhDr<JLr=0L'
    ')#Bc}@R80&&04mFf0VjpCOOc`l8hvTpj{~rARvepBJKAuhN_o=})E>HU#!bB;BCYk_5L-'
    'fR4!<G(3mG$JrKrNi8s&;$vOtSm@hHS;X|6aH`bh8VA|}TWg9r?-'
    ')PK|s!CRrFy1y4lO~!uL_X6$Qex?9g=Tw_>w3C#D+nms4clOwv5A39u7A08hq*O6uHm#6vfgoMwOYSLl>enK'
    '~O^|go-rdATK9k+9CN}zmyvzw&KzU#XK$Pnbus(G2J+L2ek|E(W4&XTJlP)@%yXpGkEe=Q`dkb@%knVS6?{)'
    '^<WLBq^LcmSmOl{%<ZBx6C-'
    'SZ^!U)0BLz%TOdLa>siID31c)ONJ>_R{OhNDF8Wl`C8@TV3Hi3ccU@3J16kWK1#c2J_T7OlKfl)gCk*1cTI8'
    'T828wr0QsEp@a6RevgO7rM&VzeuI^cEPju_VIm(jZfKgz(ZAYdTJ0>Usr}l~4nm{i4`(|FqU3x5wfN^kABOx'
    'KQtVpA&|f{9To)PgtM;)QPWVH8MPxa8P)m}K)av8K;EYZi*FykqgRQ}?vZ#J}gI|CME)0&Z(WxZKf)N~<WLX'
    '7&MKv<xm~h!GV<^t7tOfy;I3uX((cD!WK$*@K<COVd9L_6+Ei<;lnYnC}%95*vr$Nx)OB`m<u9ZevHW|pevN'
    'x^YGqiKXYdpS*?zJC;2h+wlW&lBMHpXGG(a$=KaSU^lQ~6(6p&fZxdDP?sPL(l&!{(&f4hAyxzrGy|gzjB^2'
    'LsLwXcgQwJNZv}-'
    ';`;mTeWP{t2TOGTgJAv2Nx@(z#)1aeFEX>sb90;TVuEY7fZMmTws%aFSx*_z!qF!Q$`%3hqSM`<CvsDX`SmF'
    '<std{E!R{4K*~$vRDeUr*)nQHg&NS&mbF&>Fc3-'
    'KMg4_N+J|lO;T%Wvr=d9Z(asSWoc~Z_(jhWRl$b_Pz>1WZWw_X9Tu^w%#b6!lx;+YBI*|84L|=TP-'
    '@+k40<C`w-'
    'vI=o;J0w7)BTHn3%6tT&W`8{Hmm$3g2UOb$jB`i8G2MM*fVKR6!gx^yzw#6UI*m0F~M~uyCRUR^|~F7qVaFx'
    'qmYUB3jYs8xg{LeNtGQBg<d95eLCc0O77I24ryng>&i}t?6c8sMW=zak*)==g#P9vFLy`}TMc<HIWzn<7daW'
    '`h=lg~r0j?+6Y24`j>tb1a<ceE*gl;c?zARkpH45fnC=1XO!yFey+U`@+|ln!<nzi>PmYU>EGhK>=kHZm>X~'
    'ID-Lk&ZI1`zXXjU7tbbII&8P{aU%|(pJ0YQ!!2p{9dz>FO13I=APfT7sxG7b?0qL(>?fjQI>49xHB5SZ<h=1'
    'vIACZYd2+Z$-'
    'JvJC=+V(TKa3j(vEBm)GQTvFqPz+6yzTm)mKRqT_p8Ty6NU!7+pTN?IPSJ~*=jQ%P(XGQ5bxlEz+JEuuNT&D'
    'WN+-*E`TI0J;(3Yyxojp`Ks(gSjTqd(iVqK8qR^-LHAnmTsigm^EWPOKmPR&RPVv`-'
    'vOg8oHu!9?$Xq>G#CC&9AR(!FMe+BW^-'
    'vyW~s;?@2$jTts3pFvTkn4GwA8~M{kipeUsfA1y`mK=p4VSr{rBH(dVZ-TI@P61cngZAl+sIrrko!?f3>OXb'
    'cI|E!w1*7_aL}gy;Bgzl5L<m4xNrlR7P|pJOs7<B;GlndC$%9mzkvQaGQWTl&Ih%PHrYTwj2&cuk0pnaLLF%'
    'q@>yD_qsT_j<%BxkbCa(sMp^G`<ZgAX3Fj)Z^EuE0$+H-'
    'sJ$HPwnB5}%N1GLdt(wR|gLzk(hOphNg&}PJ(1rzJtIQ9=R+}G$tv;V7A#6tn`@f`3LD*)`3&PgFJvgS{ZLP'
    'CTp-sy2g;#abDJEA8qVP94h{C@$)N<~75rzKyUPNKxeJ{c<q^B>4!k#`vVV7l|APN_1K@=WW5ru7zt3ebVSI'
    '4rnZ_)AK;x&JvR)Q$}RXYg~D=*f8w*+zoPX=glT|CJQdBfxO1yMN57ewJo4dK`OtQth&aTQS**-Q-'
    '}3U?`(MJpc3NC&Fh%0RsXo%c$R-d9)cl>m%$%l1kD#vVm`r5Xq6Rj?Wdxu&!^ro_AGhYee(P-'
    'YKB7HSc0vR!?k0VYq#545g;$#xI4`3m{GC{hI!?n#>|1u^M!fp#$3=2{}t14Et**MSg~KNsLNd*nSA23SbHi'
    '~|lRCmZ8`3NkUh?0+z^9Y&l}_L+@Uh{=f@zDn#|79+T$%3_!fNj0Dr=Y~Kot`FqSWJr)66@6z9F01>Q{}Lyr'
    'Pg*nJoogmpaLrK-HD!YxYf_D$fXS+7Vq6CD=CU~5-!O;8u#Q+_Kut3-*-'
    'UWI=Qaqfkii0{ylZ$12YnLRhY<M<&T%b_q*2x=V+$jVDGf7$*0?I#qH(lKO;an7ti?6uHq50peeA!&RjNiiu'
    '!@x}5Z(p*x0vO^@uc_&5w(!93i?~l)RBkzI4`d0N#MN25E;!lFHZSEoZu8m$#yA3fvzt?#F@X!Cr%GeTK9IO'
    ';S!|JZP5B$tvO|VLnA{fYpmOK`e~@q@+&|^ZErdTM`{bWPv9yI7I5!K^jOOU9JHl}vxXbDxybkBeXzCvx%9I'
    '6D`0bF`z;4>hWL^7S6oc-$m-_d$4A!n&?4tJ%<D`fC3FS1&O{riP7owXQQ6}rlBVo5+<<;m-Dx-ut$`lF)|t'
    'sGBF8}q?yHOdL3=2tO`xp`Ic<uu(mowen-*9}WpNYJdY*JI-(&>14=z(#pxA-'
    '3F$SF8E<eIt#~Fho%q4(P;SmOCbfDuM)(>wKxyXpq_nsb>Cb$@@we<jw{AcqLE-c9AKgH#LtSu-'
    'y+7Qc8gX}muS#!pTlW*k@UEy$E`6C$@16Hl|)PY%x&ILi7DTTZZw@sBoW`jXmNFgJ^D~&d4I6A0pm#T0)@UV'
    'd4)=Y#*^w+n~?Fqw=e*`IYu@$G36GE&no|8aki1ikseG5XYKf!4|BFtYyEM(Q1zGmo^)}xG|jrGptAl=@OZ?'
    'Ie75V_X$x{=;h9p<h^+FWJLtdXWjk4$Sgk{mJKJdC65azyJTmbRZRT93Ku+#=B$3m~j`&c*8VK!;&0Xh#xzG'
    'S3w9fu|=ECDV`8o(!a}PnGE`v?^<r!NxFwc2_fusZKh|V`sm@bwR^}Lt`My<>2&Bw2HH&hB&ZQ{9!K0XlhNE'
    '8Vk#V=Im^;uS23fK)~#&igIwl<!l)jT&jD6t1o<er4X=jv%S(}IHa_%90Crj{#3?3y~{BL=Y48_QJX_*to%;'
    'HWkuy?{ThZ~rfzkB+eho0fN&R#)}i?d<c`)0AOu_7me(LAdx$py;L);sHn^eJEf?m1>I@VUwJg{07i4f$OX1'
    '`Tx-iFO$2E|%?%6CaNNHAo+gWf<qkrmMC6RsZB!-'
    '@dTqi=4^rc=TWg4JN7s*{%@`HL^xojf$8(dfRSm@&x*A)oYN9{`#Xnk(_&&eqcdbzAf-'
    'r^)DD=v$d++=G_f|w`K<z2?O0c%6MeChIP#8bZC1tn{=&*r?RknT#1y{kkQm&Dlb80gJzvs_RckLLDqW6PW*'
    'K`@on&j9@YY3=_{YyTgnHBWt7^Zu{2rjuo!;Gjbn59$?LbewyuzNLMDFq^O9NKJAh5YW|KS5WhPD&ts*@}Go'
    '6L>VZ3`GUr&AF2>{YWvpOM-'
    '0&lta`kG_$q2Z(CEqosHIlhy^|TbsB(fAVtGTZ&qo>ZR>Phk=%lb)sEt<ap^AaNBd-me!{DgB7YF<OrQVnEk'
    '$wn1V7V`XkkWeS4EjHZF(XV24&p?385|Pz7BZj0W40<}YU`;jj%KzPPH|ml_%oV=oOTfd9PHnyEr!Q{&0e3e'
    'pxuufz`e)P?}5|eTn%vA6a$$GoOUQfCsuF3(ac$?VaRDO>s{+P?Me%1uPHC{&}b}<sk04Z$>!#R?4OuOpwmA'
    '4O|W^^K6|W<?#$U|f7?wC6&EA5{k!x3ptdc7)b>U_wf*~lP}@K2sqN}|YJ0Ap+CKW<Q(J$K+BRNPPi;RBQrn'
    'X7U`N_H)iFpX+q;B25o`Sh2!$HyF0FCn9uaN2*cPHFYK3$GVyZAq`4X4UUs7<?MlM(P!&Rh9N^dXODqm7?!X'
    'o;Tf;06+t+f-'
    'lm_AO&Nsto7gOm9ciQY~C@z5DwY?2kTZw6?}t3Dj~Q2+3pf!J^Uq1pwifMQc@F7U&9%J%~C77SOXLQN=ctYH'
    '=KuhyPh!0nQr2!<@)spF;w|1<p?9C*(0;1p5C&z_y&)HW@>I~lsB!3YqfXGEb-'
    'F_1F#n(t#cQXLbLf`W!1vDWr@vA2tl@Gb?%jk0-=Tqa-CgH&1yiiSiFGU`zp4~KL<u6_wYRL!b>hTJIYp<HC'
    'iw&F*!ZldoLx0PdgI>!H{wAoJj6emfkPBJQavl#BAO+$Wm|K}jtYN{KMSEei%M%n3*`~`wwA=5K^JKkl;gJz'
    '5CDRD$SCFX;aSpSQA8M*KPZV_lP)7kwXIz@m84o;#LZ-'
    ';dBmqtJFJ$C=4k=?4<^{q+{NW+{16uPQ2CwwN6rI4f#2&8?{aslrDPxtrTr<^21e_MIWO=c>E8Yj_{o>THK3'
    'SCotNYXU2z<&m=NftIxpdyvkkKzm@or0^Ra$UiSRC3USJ65`UZ(updr**V71a^8It%eles*bjYSZuU{yNNk^'
    'l!b#3(F^UNki!~3b>dW7?g9a|qW!Lu5L%@<?x7f&2XPQR;7`I%I8b;~`c}tr4F!j2N~$!MMg}E400E%BsJn2'
    '$%;|;yX2?!2^dDUmr#Hhxvh>5Au^yTnG0X!Tq%vxlC&Wu9fp!g(rS823H;R1jMJ@U{oB&Vu+>4M?=6ZVIoZT'
    'wz6@|`A*rm*nNqJU02%1^CS_Un<VxR<8?N-`cEKrHR=nGud-'
    '?5~tGfSr(vYX+8)s8Li+m3*i5YB_v9&3U|Iw+mEPBO{&eQkgSuz$m^4Go-hLbI<8ZEVmH7vZ9sFUkj)XK?gn'
    't;HI_lB=EXII#6DxaPv~@{E-'
    'dYHhCKmZm^#ckep@0kymL3IIas?%fClO}(SzRt?W`6&DONOi>yNG|+msj9SKr;t~WBb$<$Zzu>ZS6BNP%7tV'
    'HFD?e}RZKEeD8ras_$dQsi_^UShS;;~RJmB)sW9Gk|<aN(KruSW>xAu<-'
    'df7_#AJY?&<g2YLf&wqrj|WS%Q|oL6Ds8WXIza27tPqZav6Nn}a*1}*HV8k6w2dYRPMOSA{<aTL$TDS*4Gg&'
    'k`hU>YDZiM@CGw8?iy7{)8U$ErtG3z-'
    ')M|MoXWQbWZ?`@Sf~+Wh*U?!Z^9vT>lyXHujq8+)wkVq8e$7o<`i&ARk_!JDAZTvUVi~lo%+}f(7nzr^)zb`'
    '2;K}g)g~rP8nXD8AE=AWH=(lkZ*(bq8WF1uq`SSYRf8EG}V8~bg?8Lu-'
    'k6;NY*ZI%EDP<kZuYotp=CZh(ru28iT8;)18yHaYx|m^Xa0DKw`<2#A0Djbm7+wdzwK{Eh0)(PuE_>EYek@7'
    'k&YJ1pRU<%<PpUJF!_8!C<ppD;nQp0Ym?xOX@@}iG6HIi9wA=>T5P6FOj@%uy#j)N(=eOA6SYahE7022)^K?'
    'M*Km24HdEI}>+Sg83mb|cpI>?7*XUtoWTAwkG5$J%DGv*E=*_k-nu}7ijU&^!HRB3+MBl7{M_}SA;pXv1D_!'
    'S(4?jgN_p_NL$kQ*4f$#j>}z>px450oeDSQqW5c403H^ankiIfiLFof(d~Je~Oy6Z{=R72s7GY>Y#|c`OY8='
    'N(0B16-<o%8FX?t9C1niE_>efL~d60Z%AD=zfm-XjX{Rpmr3mkg#?X{Uld_Xqv3x>ad8@3To<EHMoRuq_!M>'
    'RF|uFfda~X6|5u)jDibfGc)96(9PtWkd}$`W<e4N@@Y}2Ghd<GOAqlJ92s(mzwV-YTOQ(bTx4VRa+@rWt)+h'
    'ZcqiRa^0)n=gY5E`I<MKuf#PS*m+gRxUM{e1puCssJ_JueFITjMeA@PJ`&J{#)E8T~8mUWa3WC_A9+q#6#2^'
    'ZmGe$Z(Dw&_o(Xg_n_I#FPl;0G9=qxNtbptb6)3TKW+K#Z(3J$0%<tomjDq#u^zUp_y9|<OS5ouQQjNrbpJP'
    'pFLqCPy+NWg^QnHVqyS4MqgI){t#c~e`QAiB#=g(&TF-p~lH740`9<7}MYU_-'
    'w1*nsprr3;JeR*Jf?4kOUeE^M6=6u7IdOEW`^MvG%!Wk4&@f1&5pVE=%l*T6WwgZ$iO8H;oxqJj%9g6+=Xdc'
    '3d~TszSEZZiH2hrHCsBznl-efyXO>GZp9eN3lWy0`d!6OJHuA7$kk`epNr)`OJX_r&uD;Bkc?_)jVM-'
    'R^TW2Q(G?TuBOjROEA|spLUvg@B7GVoIIx5a&WlojsvCglxhwr@+80H$Fs&K@5s@V(>>s!9#qEf=?atLJFRq'
    'B;hnuS(2258~u``T`bLoii5Lho!iRaGc-H$HVBfb1eAjYdR3XBhNDwnQ?T7pXG%550Oke9kMj-'
    '&$B!GXapS_1#B4W`gx;Hi!^pjTE_jvdu0GdNhBm77x$vc5+Uf-'
    'U*g_i54}p~9>|w!Ct<lGWHGhB(uC1&uwtY#v;FSy81ifBy)7c)bT=lL4_Z?Rz+Om=ET(?HSB?~rM0=VAj6>|'
    'WzkiI6=lnM^#=jEp?{-'
    '_Q%j^oI?@;l~^Mlv?Mhh?6Tj!1~JLiT&PRRkYnBI7gr@jzm}$mwYN*GS*03QnJH)Ym$p*WJ)^t&<Vx-Hf$PT'
    '(_D3gvV-'
    'G`imLqYCdm5ty6Ort(veZxKY`=iWvuujkF54AqB+y9Ii}~J(eRpU8ntGzG9_=^*V}RQtD{)`c0qM#)W-'
    't*baV6c{#Z0GiP6L(`Rw01GS0;LSv2Qm!1$#tE8yJjZ@qs{6pQ1B=SZ6P<M)pR^<+L-'
    '?x(O$*t}1eu1b4j(<7Qx?+UT9t=|Xl`8_gST#ukOx<hwk^Cc}55pr>&>m{v>p1bHtniM7Bg0pCcX9MiqZMAK'
    'iTu{_Ykh!)+%27?tpL!Mc2tk><cIRvvg9CLt7gl!PFh|v8>h{y@+RO&#xF@bw54vkHPWv`YMdJ~&J!ULRln?'
    'k*Szf6>X|DNxoEg&oJ7v}`*}E-'
    'o+~c(+>q&oB9CXFMlNOjq5|bU8Ko!}JoK`+Clc^KR8c&m(_ZS!ZXh;Ao=gc1qCHX2JfU_EYE3;M=fDqnb3&Y'
    'uiv4RsFbfuL3;6@GU|2%v&$#8QL#PI#*G3%A4R|+d?SLYrZPX4p$rS%+y|;r*tMGW%*y)n;Wgd&2Y%0Ctg|`'
    'iq&hdppuUzgA=>Zh4oDJQBTMXGy0s7$_HuPsGZOLamxDH$OYQ1qeWp5dSHpT<-TvflszL+EmIM-jk)*0M4l<'
    'Fu3h*VYC!vOS^-'
    'E0*1(f?${u&%1LF2fn99+nhbF*nbQxQV!ALQU^wEWu4kzjAh*f7Ea^Y)N=qOPrBRNZxEcV<f{1Z-'
    'W2}#PgtiU3QFzyga=}bLSol`6j-'
    '(^R|=TO>6FizAKP5%Z_6XrK_#K;`sgNW*k?@`ISShdHt4V2;}ze;Fjihafs|WC)$F0nfLMZUF~!8c`F^RkKo'
    'ez;Dn&x85FO%gYk@m8{V&jrLa+76O!D_jh2%*A!xFrR({8Un=i`xIg#?Jvt6ffDx4KhVP}6{LQU7yY7c1@)l'
    'r4W_ZBYEk+W(Ep~zq(UXDPm>6vI;e3l;`a~IrR+&<<8E~ze!X#prK*cyYY_v9xa0E|y!0`O$sl~EtK$?~+$5'
    '!fw8caHeUNds*=M?kX@$j*!0VJD0IW1<e)=(>`cXbZe;sWY|`++N%y4wy+GyGdMsATOPo#6<#gYCbFm$KrgS'
    'M`AWp`bNBqn~mebuY!vkb_hjJXC4hfzZcLD)JlfvJRDh(tvrHi<Y_C1VV%3~#*`X;MZiM}!bunRIf#mcqi$%'
    'RkA<C=7y~(>w@?!}a%rfjburSb+Dc6aaC%bp^=5K4I#us(p+7fD)zhrxY^#mhe?0l3C|tAI=??!n71-'
    '`3zeDAn<W2uF<#%A-{ztOSMF#nM%fM;6=k}JtK;5%?%fQk5r>>PVRXVn9iURgs<h$esYtL2pyFi<-'
    'K6Ms(fWvNep4aH~iXUC?$YemlkFIzZ?VItVYc?3KLvv@onH-9mVaqkrpMBFDZ?p6`@W-'
    'JT*}Ys1;eB)CNZas5lzttZ9I=Fw6P~K5-'
    'x+dM`91nHgm~ER(TAW9NccVaB_sKwMOO526WN#Vk6LA>`~CAH(=6m<>Fw~nR&t=EUHA~5zU7}3*2G3$^3Mwe'
    'u2Nn+FZ3%1t<IkpdeBAoC+~>_F8oLz9$6+5PoWkG&ETD4Hu9`Y9~A!_0etITc0m}lNq1vz`F42dzupyI9Jp0'
    'e^+7s$q<pJFR==0}tqK|HPMdF4VDNX^Pu6gtxRB8`H@)W{q62-}?a%S-gm%}z%X7;?`}wzd<M3IwdC&8-'
    'HfNg`dc&D*?4FKLXhIfg0NQ|eOvo07o-'
    'KPRYymjAwHH!Fbv>);L%uX(=}X>W#Lhc$B8S6EId&GwP`f1tNZf%2R~gi_XB4+vh{GwS9jPCSyK`$2IS_l2E'
    '4YshWOmapjRzPqJvY}3DP|O86Uxw!qI+0C`&sc@ao9)x%8HwYx+L?0nJmap<|kU{wA^H#*y-'
    '$kUsyo&YOR`yoxI#`lo5KZ37&7cXBN6zxxs=6=mWSyOaN_+#DU{BIH>+JoDL$;FPX<e2-iF-'
    '2ls_Rw|cLT2A3YB`i!7`6*rE(qLR;bzu~Y#&nX+3R!Fp}jf=gw_uUx4?T%|qk3q}(%YvD{sLBqld9r_>eTG6'
    ')nq)d!Yb3;@3;10Oui3Q^$8C1Fn!=IoYTY|P#10K|qk#!QZd5W}T#Rd2zmRa_Zvm@la6*fh>-'
    'V=`SFj(JhN~Cg0kunt8|hOUr7c$YY8l#rK(Pe`U0C#m1lq^NnWC(bRRu%c8#FqyppENQovsO!9O)W4ph=FmU'
    '35gQ<N!-7=-1B)qOx_73o^~f7MI-F0-'
    '5OUD#9V}xRWFh0p&w+4RounIqtS#$VBS?&PMNMz3KuAvaM4m0UYppo2^c8$KcjbeeGaf$&qNLzvfAfT=1X2B'
    'Dj2|Kz8F2kd)>kXvf2w%I_P<H_#lg9L}kz*p_L2H;y1?{_Prq>&{LF=ME~L2V1?;PlWOCW4=?sC6M{0&L5G5'
    '#W~_2+)9t}eHhZ9qB9SiF*WulYq)`UlqAb)_^;8lAQdn3K_J)EbGUxwu<fNsG!XML|I#Di@oAQBkD>hwnEnh'
    'vp$?eNJ%LmmFs*os<5=c}&&Y?lM=T4U(aF_Ate_37%;B#*B}4L3`9V+V_%@CCzn_ra>EV3c6Iz_Z@U5QEHaX'
    'X<`vYW2^ZvFokICG)p7t}3>Fh|m6SVn0-'
    'd*v8ERx%c3!l=t$_uIIb27%;QB@42e^Qm!(oFtMtI{@D>7~3X?TC$hS29DrBaruNM$7ADGN$q!aiK<6d&amY'
    'LW8fI6X3_$N`-J&qEpId3O|cvYT;htv5PFu*(-'
    '#*=&G!}0<@yPHyX?DhWhJ$!j~CIROKLh1V`3ae(k`Ki|R<{S}5N&H=L00Za42P{LauVk!}}gTRhX;I6$X6#M'
    '=z*=3VWA(lFY4zyaW2G@#H9MP!<1xoyV_I@lLupF-&7&=@;(<70DM+1{gcWcAxT_<M5Ie-'
    '^Arl`rAv2zJF?!WH@ZLi>Us2fV$Eud(EF?Ky`*;5pBAfjs1ivjQhxR~YKpW+ls`Lmk%~bZ2U)<GPD{o!!lbd'
    '*mw$EYCG^x2&`2IS_<2vk^B`ru=T0iKF$a7)~bt>Z_RPBE1hhfx%CoOyu_Ch-|>r%TCv-mrS#4bg352U8pC#'
    '2ZSI`SX<9~v3K?E41Sp>f!2TQ<j>$RZE^iDZPi5w5R!?NPn}rdGZ*73^J-<ggzZ&Ydqo1e;5nq=-'
    'Vf+du;bR3DEJ+V2FH~D;F?8yR9u}<xnElV?M}7o$-_yv0bU$gtsLM*7?lk0-'
    'n2kjdRK>p8Awi1+|QvqJ|Lcg_*9Gn#;&(P1R=HcVO>c=4ILn?y_1>G9tFSN(lQVf!js?&&4hT?4Qv~@Na%U)'
    '*XQ(c^C^(f$=&>96OLkflTCoB+g{BK;@?=!Jop7U66Ue|^^6=VTy5$7jDB7eVui>*(lLi`^_2V>%Gp{yg`C*'
    'f4q8AQ<~;EXp6{kGn~+P%Hv#nYMu(dM#Mi^TQYQ`$cU^A-wihTYur!9m+-'
    '91oG0@kj`y6V%VQgb7`O!O!g)IMa<S^D_A*CU^**#ERBQ6?Rn(3{WFPVElZ5vq)xPLvu!vPJ7@K79VPig%H2'
    'T*Z`B(Q(m;bJ=tqjB5bbheq3E(=}2;qKoMhdC4eYgJ&$1mm`TWJN9aJNsAgU($5v`w$>`)164kDyQSNmq6_i'
    '`%0wlr>r>FnsU#K9~VhzV?-'
    '^27+g3HyMy^gqAS#IDTsjQIjzJWx3ZJrkg#{mxC|v>wG|hoBtNsE*6s@dPcIF)zl8|y9B|`SyPAL-'
    '?_RRjIm%AjCVy+&WTRPai~_u0PR%;88<?(oofrY&$Xh4kNLSlWobAw?-'
    'E7@47RK_?Abcg(^EiVVZRsDtZ9NuefCeI4m{C+uGvz-a!;4OE=4Yf|%5K*DjP?%y-2hrZ-'
    '^AQ|LWXFY7zmW!ASwc+x7Nqd;xXy3?le4kM2G32kUe{n;J0C7$rvsai~9q1G>QfsW@0g&v%`Z$j%INeNSTps'
    '0(7$MBc{?2{L%o<Hs;k)DE2rM9S`nH{ffa2#qlQ$-N94g1*{nY-'
    '?!da0fvyLn{PmM&MvS7MMu5>e#|1y`%t+<h_ej{Z<@mmCq#W?Z-'
    'Sr2`Nl4RPt(4!M{_|j2@6iDa}q;)g)9X@I!Jj!rGdU7T@kL}>YUwnd<S>9eaH*CLF{LTcUUZqvaN!5$eX}#q'
    '@-6tBmM+KLUJ4N8w}K()rfzF8S)LwUWT-m_85`-'
    'RNKj?rbP_>)5n_^F=Udu)@(M=&T=FEDNEl@Z^X}X(2Y5Q<qaoUmOa>XPN1jNBzBO4tPV|L<E`|gHc9M3Guht'
    'hZ`Nrfs|y{*D+V&7G{dxzA#bIGfz5l7;0lIll4r!{tvJYCLn<zF+4%9Rk?baTitNoyPcU}PaJroazbQ5nS6c'
    'd*H^2tr)yzonKxQ>l0nw8N0!U0oHS-CM(XXc-Bo$4V`S|S|#V|!Ds#<CY(P%>IBz74@YuH@#GKgK@T=N<nNt'
    '$4s;3a=~9<X?NLlBVo(jKrr@JH1eEBNYn(ZTlzm$~1!MnfY9;y5k@e&0G19GLMpzaNe)h_^og#}|!sv;)}Zk'
    '92$wTrGX1;}}GF@)LeBZsr<j$-'
    'o5{W)r@2xj>eg&r^Eda{~lfEJ@b;44EzE@q1XZ)*EZvZ6v#5V{L0qbWc*O?X;QfO#R;aBTp6<Ewo&))6oTrx'
    'wSy&DG%5X2OXFGfc3CJF~&gN&F#ab8R(VlN2V8)j%t~MclaPC98BLk816KVEDeUcGnDHM!qq1j?($v34lsR5'
    'HB$vvF07*?phL)lq5<KTQAbDHz%X?b&>Tp6M8`vfwqDJ+;pH2b8;65^{HKi9z&_b-'
    ')9;|AuQuJlws)G@0b1rf3-mz1q%BEcJ9UnA1PHLJ37MG3g2CTqkNFq4X7)JqRlrVKC-'
    'd(PvLyW@Q=yagOaGWVEYN<+cdS_;#c~07hm-=mL<g-'
    '+DPSX^NlYuia9f%_iTxa&I$PrY1e+J_=7vCk`|FI`;EmFYOxqZGB8D-'
    '8wp>fKu7~iEPFs_ZmPdef`qT$zBT^LfQFMlBGX!SB8ty8XCD&&74<a&s22F=h44Xj#6#?%QrU%?7@h9du+%@'
    'ATh66T|_7iiBuNP2*(@!zm;k`0fGlTF0Q}Ko`oMc93Gwz;1V%7e}^<aVC|8Rf0h*WXIkSLP=Rc1pA$e(4sm;'
    'ipMZ#ew{l4|;JdKIF)&2ahvYxfxgMzVg1!$|gC;vkYQd*-0%FK=Ymc*!trm|+a2^kIfMK&u-LGZ-Pf+b3`v@'
    'v~75BNBnCQgb`FL)qt+ET|8KqiiF<MfndLFTlfD4;)M29a0}S`a*GQHq721NN?y>zB?`k)OZXKG1`JVc5)sC'
    'jnz#glPo@l{^Gj;f~=H}T4M}kj+n#$XP`^vn~*)oI{lQ5HIuy!PuX6x&`+D5vhg<Zar;{9Bqy1aUu0_KqBBY'
    '^aRmar@-i+$AdA#7+<A2M7;d4H=EslWTrAy^-'
    '_2NOAiw0^Hl1V0!u;vx$qXG_n1r`|GcgkU*p~#qyrhvC!35KtH9|rRNRdXI$@G3^*pE?OM=^;M*U@zl-'
    'r02&$q9rv&Q_(}r)|JxZAUR1ArzZ0Hetr@IxLvKix2ZnaUtcu{I9rL=sv$0V3Gfr?}oF+hxulpwdlc?8|n1S'
    'g=`&5zAs#l!8gPI8wTHuq#hQ~7O36$87y7yKF7lg1>9Crz~-9h=IXoVM^-'
    'vnO0x{*>14f=WivE@jn9~S+vuzLdB!~gt<`Hew?G<8Z?H|ABu6X2%v%s!z+Sb}lH@3O`F<qW*ft_b>^vY&+G'
    'RuhGa87?G5i4@Ov^ER3U1BIF*Jc-'
    '>^q#I2pvw{0u=g3%t#=M1Ir8_!h3d{ZnzAMcgkf$1cYCB2pfan4I9YzfiM!saJM10Vtgiy!i@M}KF!Cp3Tb1'
    'YWeQHZ9I<qTAB)FW6<j-h2?Ru83m!FfI6ntBWW?H9`+~`!Mx#4>-'
    'Z1ai$*f|ZX}?Y<v}$Ao?fVFcgZoVvB@XUBNtL*tWU?@F3Re#JX!0@lHauV}&6o&zCa0rufQz2)^}qrm(C&c+'
    'U#wjVWAHUw7_;!DTNoeXCUw@h9I)DH6So?`-'
    'K3W540JD=a6w~5g8^TvkDewZ+>F0Tec&&GG^oQ9Nal6)T`*^wkp<DVt%rT<3HdRp+*tmY)G4Lr^2c<$xZMKU'
    'A<=Bx6(C<}<Lq~yl8+<C*^{5s9r5Grqo0#cnlH4yO6Z#WI({HS+IJq#7eEw@TMAD^$Any9p<gV7f`p%HbU$F'
    'Lp(^?wuopmUIgK4k>9EpP><LIk{uDzRgm7U71K0`_IGAk^$pw2T?rP25Ls{S@8GGnhz;B0Y<`&eY<YGfM#BM'
    '_m+Y7=we2+02*Kq6(#&yNWATNm<Y3UB;Y#qsChR*xVHVHx^M{-'
    '^PJ9d+tu^^h9u>(g4w4Ds80dh&M6BBOFF;1vvfzoNtHXsVNI^PFIp1jt62w0ofZ$%4AZW3?4$IvUD@gT@5*='
    'XrupaZ0GK9QqKd*<<HI5MSsM_x0LrJXzSyG-'
    '=m>W=(Wp1hyk#s=ZNH#L%vbC8>PpP5HG$=JMJrjY`@uBEZ7?Bv79G<J=Je%vmN9cCsw(ybhFkAgg-hb1$MSD'
    'Uc5HjV-'
    '3_7A3bnn=zWhvV0TB8@jt6xlK;sSPc%Ju%XcQ;KY(d9plTF`swR9cn69Y^PJwQ#oK8ZPQXYNNX*#H*;qg`c?'
    'ULZUaNkbj&lp!O$jNn;GcT5oNA<pn(?3OSvh83>?x7EA8N@ku0X7&;k}qO6+Pz1P68<PG7~Zcn+trxKM6&u<'
    'mB8X6hixf(X)@)%CRIW<9MLRZnZW)YF<}^|a<lJ*_!YPixN9)0)FbYyR-'
    '0azR=H0%=Vu*9#I_*Hol6zYP4?Is-f|FSUAb5cyJ&&*bFs7Tol-'
    '*tQUusDGm)3*shkqvJ6IQ>Tp%q@b~}V8;Q$EW_AH8v7V3im!le2Tg*slJ(<vH2+}Rz+<*;#$k(?9%-'
    'Be&)5D62*@k(X4G=x%|-B-ZR5?jk|%wFaSS|W;|F-'
    'Lmz9R(V33|jp&TY|Ig7&&NywG#EF8w)ZFm)ISH9cO8jM!B+kliXf49L4P{=-'
    'H0MiFDzcCyJE&Uq<GMKb)4116#eq)$or_DfAJ4jsSbi;pufetAkXanD;3~2Ep=6yO<98ULvnWVuCaNGc}jXh'
    'wPm}VRpZGihAHy^p+P|kx~a47dV@|mIBL^ve=oUu|M|23Fxioq|*%tq=G2>aF;3s-5_-&l<-'
    'pucen)|vhgm^1~%Km%!-X*O-Z<zYo2XuFV)P-`a7H7_vGH<f71b6kej-W-dQMl+09ay!L=2L}Ex4^-'
    'BBphvw2w%2>$NxcWM>OIh+-'
    'UIjRJ<z`11MTZQ(7xUS^Xole<$@lFB*Q5tKb<jjfvl%rHpGF=lP?<vpd~NYTk>+fC70D(GN;~>r|K<fW`dTS'
    'QE$m9^_J{WZ^^8BOP;Q`<g|KAPOG=%w0cY4theOqdP}aZx8#+2OHQb_<b--'
    'lPB69xk3#^ZgMBj31??ln1}TZ$AIpD&*un^y6U9p$uv<<!%7swcvS~AJ477<+)l4wQHvoeUsyAqBQV-RzdZ;'
    '$2hibR~x1sv){{^al;fJ8|c+ASu@?Zzz%HyAcb+AbQTZQKFXsdP}TPHA5;ceRsFiXL0+uvZ8|D(05kB*|s^6'
    '%AGS5;S4cUONUoleq(5FmWz0|LaTq0=EBbVB$@2nhrtfsF_lLWlt&gNO=&1q|#MAqo>AGJwD$I>@pa7S!ReO'
    'cptg%VAMj)^!mbhe2dxE3o&z+WlvC&z>{q%wP9(r>pzDcYp8R-'
    '|ya6m7;I84}g$7(rfRA%$Igs9Z<>V@%;+uGu-LO>55J5CNP4+4((HzL-BEK44&up>E~c#Gw0}?9F4>Wj4?dD'
    ';^{TsLwR|`&g5l^9W=uZcc~pV<woy41<3J}Gp;Cr-'
    '3g_q6xeb3g<bLn8<|nuVS7iWE4_K*<2G7r1<)m6;D??rJ|Ti+U0ww{fTIO*<u>qQz4sDwq-'
    '^hc(L>0_Y8E+TLllxHj*w|j)lGT5N>_|uuCB3@RdJQ-'
    '%NkujI!|4vllFq&E5x9yqE!l@uRMBKE^yM#@Wc0X+FmdmoV&zgMImy9IoGTbFtWHe3NQ($xnCFnSEruiH$bk'
    'fn8Ux1H)iE>DECAEm*dA-jxYF2I6n5j91nVACYaqksgA4{F|JkI5ih~7SDa-iA8Fb^f~*ZzgCPt20c9<c@?P'
    'Z@9=cA4$u6}fJC__2?06?+s(_5QwiS>JKi<k=rVd=-'
    'O+18ffyWX6M8zEdn+OYzv4Rb}=^)8v1F&uB*mx5J3|;KA$fEy!0TJnM5Z9P=oi9rS_O;Lpa>hj$2eL%i;2Vd'
    'p6Po~^6^+tvP-'
    '{~gB@jNzC5;l~@FR75)z9H?m48%6!miJ4WbmF7)X)S6X{+GPqyw6SZH$j~REJX*8!tJ@g0fS_Q!u1rFa}j4r'
    'wsVA*t~u>UN^tZgJ$wIj|7*O4fx<^V~^kQzXaPN?T-H(R#r6sEX-'
    '$`Ux8g!p!v`8bW}w1V?HZ81BPaVs^Z|)aQBtCDxOaBw8i6cdRl$Bf}T&j0GGGDK_BSkJ-'
    '!q#CZe($4<w?dsWl!*L`_p_Je?eADz5Q>tY|B2@O;A4O_61uut2sIEb~Yr=?pLPOc5y>faNSOz{2KD?seBY$'
    'g|N$+y@=BBYMVs;2`_QtTyjE=<~@s7&6;m?SlAM<vnG5pwZ5PQwDhK<?ty3{I|WvaDq2i1Pmwm_RZjYgL(R6'
    '9Y;NgvrLDEZ`Pbw;UgP^=T&w=P{Ye>gBpC<i{YRKL#hM=L#i!&(!SV1HkaI1dmVIlNuK%u#xnc|CD}<<0NP+'
    'IGa<CHu{28T@<xe$*=Za5>eDv%Lx#l0vR-'
    '5u909moX5ljL&%$Mgh0Agamok8$bbxEOaM^3&GVM=s`J6uq6g6EMs1bLe9B7nso#fHdMhPx(L>Lld^DOMm&1'
    'KlD{zCg51k>_wjF$mCqfR*50X#!aI2d^P4FpeBzrn!MZy<QUAb85xI~aK4oD4j>oD4j<E(V^_1_MtQ*5lsue'
    '2n$DgTAX8f~VZn06fbpObx)ZJZfsdVwy^V+C-'
    'kLEKJp2;^_;K4DCCfbQEN0Ck3)IoS_9oiUvGY1qO8A{K<`W7}<+u_tm`)x}|)*de=b?W@o8)9CY2F%gSv4Pa'
    'vQaIOr^Yqx5$g-Dx>&hvl$N%VDjS!+!ZE4jTy$d)g|9#FJZ0NRPRQnKU-xAI0$yCyQEy@3FFImFS+bN^}V_h'
    'g@c81~(tGN;Mb2x=1yLB0F5o<!Q{|-'
    'H`>k+&_a)C#Rt^W5ul07V`=A@#w{6D!4BeC)oFcH_CgpDp>gPs6jO>v>Sb(J0elzQyVCvX&OEaB2b}z4}&m|'
    'Tg5dOxha25>Dgdd`I?g5o;)nBZE@$@_X%Wg!YzA`M2-%-W#4L}$1`u)eJbfKQdI!-'
    '3uOT%(ICspKeQz{NomCr+gT^A^WGBx26H_3gp)koUwT=r;>kxPX^^YPo}xXrB^-'
    'UOcmw<%*^xO47Olxzw9%x~65s&=1Ym5~XM6^wLu-'
    '5Za!Lv(P6tCr3_H!itC4Xg_Zp!~J<aqX9_c^KV^N^sFrSQ7q{BSun^<8n4}>Z<&Bt$oMVoPe3j!i5TR9{~l_'
    'qx-UzuD2fOe+IEykyoJmf9`pvSG|k!2-@g%7a<bWf;o(|!JK;VqLa1vAg2D-ybe&s`vo+QhHm^2$;PBGB-er'
    'PBBKumzLt4(|c265SHiAk4?S9oj`Fo}Dm$1s^Fp@94lv$a%*?AQzL)J9@w^X+C`d7T3<&k)4}Y@Fs;=MN~oW'
    '%-AY}sYq#(0ZiHXhV&*(y5URlzymUA%+JLxP>e|pmK=AHZxorMpQlV#WsdChzi0=+yT$dPmMW6{-'
    'X1;2M&1kc=zf`=9@eAt3OPCUfCh?jZ?xAwpwTU5g8hb0)<o|qpcpgCIu)RkJL5{Few{u)rBs4_{EHb&Y`{nU'
    'sbr*lnxk(PRl)C(Q$?e}kISvrz+fV4Y%tgD+kPOi;2L}3L(-'
    'UOmCmbK={(CSoo}kPng|}NiC`v)xLaIF;=kcNDoJ7@tih-'
    'j;eD9y%)e+aA&C{H3$JQN!7Zhy3~VVZIAvf}HF30o*JbN0VV2y{ztQl4Jvvqe!bf!chZgx;b*zr&rt9f|)6}'
    'chZ2#Xbz++YyV6xQ(DEza#0ApZzo2_J!O)j$7GOH9~3yo!77P0wVwpE-'
    'C%QU55=*L%M`D3tJL!RIsVupBvJBn270)L%jB5%8;?pl%eUf{8E7qQgc)T>x?ofvnQLfqfvu@Z&n6iXEGH6p'
    '0rhB(Gtro@NDV=gi?wOMQcfKO|b+MOgFm<xm^1JVYl=A6NIC5W|#my^#rNztNaIp0MqYop3|lhh~8XO8fxRu'
    'HRDk(f`oXvh6H`=T9t2{kbln>vqHV4R5!>QunY3yoGD>SXK$POf**pZPOvLk*hkc}rTLlW??ATB?z$5V1GgA'
    '>cQ{0@5<bT>zMc(>{{$WNlQFGf+5Am$Nv!I{9zpY>rF|T#)OLyPsDfirn$l*^wRkGhoG6u)xHRAxsy=rk6@s'
    '0V{bRyo7z1`7D|j@8nGD!AnT_M?z4CtJ4l}_W`EijY28F)VoobVWY9Z8-'
    '+P|Mk|glhJ9bWi%v#l?Xv2qyXfBnc5|+A0jw{+Ayv8o`cGgTbyCSy+Z!g$FZxt=m?ToNMNM^)XN&6WsV=%Y@'
    '30Q9*830ZEpFQ4Ijl=w@>iaS#`(!Mf4-gb(@nu+3cOl0tV-GKp_6kyli?$iOikY7CB@0dZRdbOXLZTrkWlxj'
    '<KkfFL^OOA-)=N{K|8HATJU_@8si-H&d2H~FbCJD9pDsSwYJ#~k!-$k2qsoI-'
    '!NdBkIXl2Vb7^W*$1l>xMag#)nh@HXR38_U3yxfI|A2Kprx+_ZpyF&3QBKCw;<(~<VX;RE5}_E7dvT9$`&wW'
    'DFoYI2iYEXlRsvVri7b3K&vL@CJ$k1_9J$2sYV-$bEI!ol3VP6B-'
    'Tyo{$Q`tP0263Id;gbhyB&sJc0BMs@5t+x_5ZB29aaWxZCPq%Vfut(aIkn20q>;|3RVeCQS!JHu}D>EmUZ^C'
    'm`$-=xLC~kfytfPuesHsHI)-3#5B+CZMCm+K)-(1k3-'
    '6RB<Za8k8lnqWOFQdxMqVGBF$~=dhI(ENA;M!N(&Chc4n}07+z#Mcfv#3iCWmG^AP;=EMQc1*^WuBi``9w;0'
    'm5pq{+fnTZo59o`%)U>!GB*KXBu+pRjT!0Nd5f;0xJJ4<Y39KDhJj;)d-kNG$mq-'
    'w6`C%Fp$XF`keTV!5cGNKs5awd#=Nfu0Rr8T|B|GVi}e;$jivAFZB_c&S+3-'
    'H+mz3lnnRb4!8h4e2ttYt3yf`b$k3(aA(Og+N`m53Fc;jg0rJj1_<a6e<w)73m?<?>5hw}a*aJ%tRq1n6lC('
    '$jVpbvz#NRg<3cej@<QdCh%U7;ur3p)&Dpthv=m2`;i{Mx6u~G?&y#Q33Wn7@n*sx*)lDdSs>sdz-'
    'Y5D3e!lv?SzIK&;OWY*#!yZSb#GkMLxz*VHC~$S5#1Agi5WQ@aIltL;+(=PQGK>UU1so7k#h@40q><@S^dI-'
    '0>%2EI8*aDIoL5}dd(g2#+o_^hR4jQNI-88GRgV7fUnESl%&=ID^%K`<o6UFY1-gD!aB9D-'
    'tWE9*qNIAp%t%*S+4*&E#JG(3hIF|~S1@}rFT4lOY?Bs+5jJLud*?*wHBu+GG0*@jQ)Ic{4A7v%4f@UH7nHh'
    '8i1e_F?_7SW5?7Qmk#Jt^Ud_%eqS0xw3hL?+KR@R(xLJGiIdyAnIN4D29>_%d)`QWNuHq>29ovD(B}*qM19L'
    'RiU4t{)$G*Gw^Sg6YOvX`3nL*70}v&oFv)3Y)=r1Hv07dBz_QAceFH3J4Qiq-~-'
    'if^=J1bzAH=NYX4rs)m(|f01d8_%ycSgVQvu=J?WpO+jjoX}^J`p4R5TqZ`pSM-hb6aGOJb7&NY3PX~4z9BB'
    'tO8*>-'
    'Sj6Z3lSGhvzwS;>LwvN4Vc1VO9J>}XFf$Rx}^gl}E_=u1`NTw&UL;6)ad9Ab^na@A?3~8!Pw^bPuMD^DT0}5'
    '>4<r5aemyw<!V_|upv6eTVNUTbdvVpbAYA;eI&@NIY&_Yb0)r72l9<tUh#3#Y%i_1ATOt%uYJFML-'
    'NFuOy)0^p6xOP2k?R;Tt?d||CB~9^nc-RQblJD@lTx41HMWNA27tT5;W;jT~%!6V%R;#mEQVm>YCh@Wg8)%z'
    '(S<N!ZJA+5se}`>~yR4C1yh7XHB-'
    '=}h^;}emO?m__ue)F}UAUN)3Q`ukC!r%2yT8Ip<RSMsCi>hL!2{8l2NQL4vv({O(mH&{AsG~P_<SlpEy?!^_'
    '+#Qp@5ds9x^DMxVF|nkTsHu3@z)%<SW%Uk@~wI`c8inLp_IOmoTPq@lK3F<*R4r06_{2_B&NR1)8*lq`kWoa'
    'b4-0gCo7A(6(I5L#W&?64!U_rzWkPh)W^5lzBYh$^@)W#eJ<K3!jeB9?i0ZQ8){4xZ;b)d#+=h2GFMsUt-'
    '(5xUA>eZ30!ieaiq;V*E|a<#q*Qd0{q#Z=gE;sZ(5$`9UDEEmFM|)h3w03GW&JX7Cq~PNPWoHr2|sdmvre6a'
    'd#HxJ7E@Wlh!!<DOr^{4v^Ajh0_eO-TwOrup?q>;X``JlY>RUWAO)7<onZAbqA$uOD@?)LL#mHiO<4v-'
    'dJW**Kx?~CIM171{gfRQW@bu@y2q$<?zHyN)HdFVQ@hBiYLkAuLut~dNiTjHV8TLJpt=gg{y_P@yx)xJa#K4'
    '&Ebza=oEiB*KN@M^dGV6RY~Gc=<&T+7wGo2A>Dgp(3e=Kik1CZdeKQ%ltygu$*Dy>@-'
    'G3(voo|`!3Bc`EYqZ8%F1guWE4m3j8xA#tS92>+mMc2E_sOtW?@o9%hX9`aGxD=fhU|}hv>gK;8flQ_!NA?I'
    '((5=wGO~dX-MA$vrTN$H{uzd(FRE60XNWgc+;H&i@VBdQe~5B8*5VSvzk<wtR~eZt4Vc<HL0RqR+FlaHK``|'
    'iC^(FtDsLDpyXfjc^f3dwD`y5-8?<-'
    'JA({<n(ya$!g<94f>Pz#yfDMdqpNw0v~_oBHDGD!T^fX;q@3ok+Bho2Kfuy@h-as5LOiy(!Qf-'
    '!BL_GnwG|Ou@mTeB2$`@t&(PK2jk&E9n})T`^d#*5NjG_l|4O1$cm;0`2@4;aq&Yq;G@G<JIV?yfY0ab}$cU'
    '$BH;5CRB!AWk5n_mQY9DJ^&Fiz6b&j32tm5q0vhou92jH8bYwYuow4b$OJ9GMg){eKIh7D{|mcMRPz;L5C3}'
    'kjwhB*N0vB)q7YiA8}uy)pXSn<_X&vyj5&4j1lDPYGEAk_3D?DHe^>V3dC019_~n-'
    '~Ce&P@`xi)47^Py7oKS(=&7gHvMZ>HHypdV0k6kwUh6BDU8xx?)tsb^}jTd@0sDNM}_N7}}QEBGluP{CfC*H'
    'ONz59}oz-%?q0XChKdI-'
    'oVE>nYK}QbNwv|fEbMXNLmUaFMW^A1yi4;s`p`4YgH95s8Cgu;2ATeFJ<~<TrO-8Qd&7(Hb9Bb-XNcm=)&3y'
    '@_$HVn)iKWhK<Z|x2at)PVWizQy8@;PkmP+v)qdnp!Z3@q#W?(f<AREHkbR<ZxA4T>Tm9|CrUTPuxnytEpe4'
    'x7N7lr9`-'
    '+wp8bLB2yB%P{YW~7Zk7N3K7BQ7s|<O*W%6xttw4W0cO3^3ZY9hRmU5S89e3?Vvd!Bfz;zw|{{lB;^zZ'
)

_MASTERS_CACHE = None


def _unpack_masters():
    global _MASTERS_CACHE
    if _MASTERS_CACHE is not None:
        return _MASTERS_CACHE
    data = zlib.decompress(base64.b85decode(_MASTER_B85))
    off = 0
    (ng,) = struct.unpack_from('<H', data, off)
    off += 2
    out = []
    for _ in range(ng):
        cp, ch_ord, is_uc, lsb, rsb, nc = struct.unpack_from('<IBBhhB', data, off)
        off += 11
        cs, fields = [], []
        for _ in range(nc):
            (np,) = struct.unpack_from('<H', data, off)
            off += 2
            c, co_ci = [], []
            for _ in range(np):
                x10, y10, on, co, ci = struct.unpack_from('<hhBBB', data, off)
                off += 7
                c.append((x10 * 0.1, y10 * 0.1, bool(on)))
                co_ci.append((float(co), float(ci)))
            cf = []
            for i in range(np):
                prv, cur, nxt = c[i - 1], c[i], c[(i + 1) % np]
                ux, uy = cur[0] - prv[0], cur[1] - prv[1]
                vx, vy = nxt[0] - cur[0], nxt[1] - cur[1]
                lu = math.hypot(ux, uy) or 1.0
                lv = math.hypot(vx, vy) or 1.0
                ux, uy = ux / lu, uy / lu
                vx, vy = vx / lv, vy / lv
                n1x, n1y = -uy, ux
                n2x, n2y = -vy, vx
                nx, ny = n1x + n2x, n1y + n2y
                ln = math.hypot(nx, ny)
                nx, ny = (n1x, n1y) if ln < 1e-6 else (nx / ln, ny / ln)
                cf.append((nx, ny, co_ci[i][0], co_ci[i][1], min(lu, lv), ux * vy - uy * vx))
            cs.append(c)
            fields.append(cf)
        out.append((cp, chr(ch_ord), bool(is_uc), cs, fields, lsb, rsb))
    _MASTERS_CACHE = out
    return out


def _turn_deg(a, p, b):
    u, v = (p[0] - a[0], p[1] - a[1]), (b[0] - p[0], b[1] - p[1])
    if (u[0] * u[0] + u[1] * u[1]) < 1e-9 or (v[0] * v[0] + v[1] * v[1]) < 1e-9:
        return 180.0
    return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])))


def _contour_defects(c):
    """Check a single integer contour for kinks (3..30 deg), short segments (<4) or convex spurs."""
    n = len(c)
    if not any(p[2] for p in c):
        return ['no_oncurve']
    k = next(i for i, p in enumerate(c) if p[2])
    pts = c[k:] + c[:k]
    seg = []
    for i, (px, py, on) in enumerate(pts):
        nx, ny, non = pts[(i + 1) % n]
        if on:
            seg.append([(px, py), None])
        else:
            seg[-1][1] = (px, py)
            if not non:
                seg.append([((px + nx) * 0.5, (py + ny) * 0.5), None])
    m = len(seg)
    orient = 1 if sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(n)) > 0 else -1
    bad = []
    for i in range(m):
        p, ctl = seg[i]
        q = seg[(i + 1) % m][0]
        prev_p, prev_ctl = seg[i - 1]
        if math.dist(p, q) < 4.0:
            bad.append('short')
        tin_from = prev_ctl if prev_ctl is not None else prev_p
        tout_to = ctl if ctl is not None else q
        tin = (p[0] - tin_from[0], p[1] - tin_from[1])
        tout = (tout_to[0] - p[0], tout_to[1] - p[1])
        if tin == (0, 0) or tout == (0, 0):
            continue
        ang = abs(math.degrees(math.atan2(tin[0] * tout[1] - tin[1] * tout[0], tin[0] * tout[0] + tin[1] * tout[1])))
        smooth = prev_ctl is not None or ctl is not None
        legs = min(math.dist(prev_p, p), math.dist(p, q))
        convex = (tin[0] * tout[1] - tin[1] * tout[0]) * orient > 0
        if ang > 150.0 and legs < 15.0 and convex:
            bad.append('spur')
        elif smooth and 3.0 < ang < 30.0:
            bad.append('kink')
    for i in range(n):
        p, q = c[i], c[(i + 1) % n]
        if (p[0], p[1]) == (q[0], q[1]):
            bad.append('dup')
        if p[2] != q[2] and math.dist(p[:2], q[:2]) < 2.2:
            bad.append('short_handle')
    return bad


# Weight model. The master is the Regular drawing (lowercase stems 67 units, Latin Regular's 66), and a
# style whose Latin stems are SV times Regular's gets fraktur stems of about 67 * SV, so the fraktur
# darkens across the family as the Latin text around it does:
# 1. the outline is scaled horizontally by _sx(SV) (bold fraktur widens its letters, which keeps the
#    counters open; Light narrows a little);
# 2. every point moves along the mitred offset of its two edges (the control polygon's offset, so on-
#    and off-curve points move together and straight stems stay straight) by the rest of the stem
#    change, with vertical motion at _AY of horizontal (the Latin horizontals grow a little less than
#    its stems); a hairline (thin in the master, measured by the precomputed interior thickness) moves
#    by _HAIR's share only, so the fraktur contrast survives in Black;
# 3. a point moves at most _CLEAR of its (widened) exterior ray clearance, so two strokes facing across
#    a counter keep at least 1 - 2 * _CLEAR of it, and, thinning, at most _THIN of its stroke;
# 4. where two neighbours' moves would shorten an edge below _KEEP of its length or reverse it (tight
#    inside curves, notches), both moves shrink until the edge keeps its direction: the points keep
#    their order and the contour cannot loop.
# Point counts, flags and contour order are those of the master in every style.
_STEM = 67.0
_WIDEN = 0.22        # sx - 1 per unit of SV above 1
_GAIN = 1.40         # bold offset relative to the Latin stem growth (the hairlines grow less, so the
                     # stems may grow a little more to match the Latin's darkening)
_NARROW = 0.06       # sx - 1 per unit of SV below 1
_AY = 0.90           # vertical share of the displacement (bold)
_AY_LIGHT = 0.60     # vertical share of the displacement (light)
_HAIR = (16.0, 0.30) # interior thickness at or under which a point is on a hairline, and its share
_CLEAR = 0.30        # share of the exterior clearance a point may take (bold)
_CLEAR_MIN = 0.12    # ... in a counter narrower than _GAP
_GAP = 70.0          # counter width kept where the clearance allows
_THIN = 0.24         # share of the interior thickness a point may give up (light)
_KEEP = 0.30         # an edge keeps at least this share of its length, in its own direction
_MITER = 1.25        # longest mitre, in units of the offset
_BAND = 0.20         # share of the height at top and at bottom that takes back the vertical growth
_SMOOTH = 4          # passes of neighbour blending of the moves
# 𝔰: its hairline diagonal runs between its two small counters, so it keeps a thinner hairline in bold
_HAIR_BY_CP = {0x1D530: (34.0, 0.0)}
_GAIN_BY_CP = {0x1D530: 1.0}  # ... and its stems grow only as the Latin's, so those counters stay open


def _weight_params(sv, bold_knob):
    r = 1.0 + bold_knob * (sv - 1.0) if sv > 1.0 else sv
    sx = 1.0 + (_WIDEN if r > 1.0 else _NARROW) * (r - 1.0)
    return r, sx, 0.5 * _STEM * (r - sx) * (_GAIN if r > 1.0 else 1.0)


def _edge_normal(a, b):
    ux, uy = b[0] - a[0], b[1] - a[1]
    lu = math.hypot(ux, uy)
    return (0.0, 0.0) if lu < 1e-9 else (-uy / lu, ux / lu)


def _displace(c, cf, sx, d, hair=_HAIR):
    """Per-point (dx, dy) for one master contour already scaled by sx (see the weight model)."""
    n = len(c)
    P = [(x * sx, y) for x, y, _on in c]
    disp = []
    for i in range(n):
        nx, ny, c_out, c_in, _min_edge, _cross = cf[i]
        n1 = _edge_normal(P[i - 1], P[i])
        n2 = _edge_normal(P[i], P[(i + 1) % n])
        if n1 == (0.0, 0.0):
            n1 = n2
        if n2 == (0.0, 0.0):
            n2 = n1
        den = max(0.55, 1.0 + n1[0] * n2[0] + n1[1] * n2[1])
        mx, my = (n1[0] + n2[0]) / den, (n1[1] + n2[1]) / den
        ml = math.hypot(mx, my)
        if ml > _MITER:  # a sharp corner: blunt the mitre rather than grow (or pull back) a spike
            mx, my = mx * _MITER / ml, my * _MITER / ml
        if d > 0:
            t = max(0.0, min(1.0, (c_in - hair[0]) / (_STEM - hair[0])))
            share = hair[1] + (1.0 - hair[1]) * t
            clear = c_out * (1.0 + (sx - 1.0) * abs(nx))
            # a small counter keeps _GAP units where it can (half to each side), at least _CLEAR_MIN of it
            cap = min(_CLEAR * clear, max(_CLEAR_MIN * clear, 0.5 * (clear - _GAP)))
        else:
            share = max(0.0, min(1.0, (c_in - 16.0) / 22.0))
            cap = _THIN * c_in
        sx_, sy_ = d * share * mx, d * share * (_AY if d > 0 else _AY_LIGHT) * my
        mag = math.hypot(sx_, sy_)
        if mag > cap:
            sx_, sy_ = sx_ * cap / mag, sy_ * cap / mag
        disp.append([sx_, sy_])
    def keep_direction():
        # shrink both moves of any edge that would turn back or shrink below _KEEP of its length
        for _ in range(60):
            bad = False
            for i in range(n):
                j = (i + 1) % n
                ex, ey = P[j][0] - P[i][0], P[j][1] - P[i][1]
                L2 = ex * ex + ey * ey
                if L2 < 1e-9:
                    continue
                fx, fy = ex + disp[j][0] - disp[i][0], ey + disp[j][1] - disp[i][1]
                if fx * ex + fy * ey < _KEEP * L2:
                    bad = True
                    for k in (i, j):
                        disp[k][0] *= 0.85
                        disp[k][1] *= 0.85
            if not bad:
                return

    keep_direction()
    # blend neighbouring moves (different shares, caps and the shrinking above) into an even offset
    for _ in range(_SMOOTH):
        sm = []
        for i in range(n):
            a, p, b = P[i - 1], P[i], P[(i + 1) % n]
            w_p = 1.0 / max(6.0, math.hypot(p[0] - a[0], p[1] - a[1]))
            w_n = 1.0 / max(6.0, math.hypot(b[0] - p[0], b[1] - p[1]))
            w_c = 2.2 * (w_p + w_n)
            tot = w_p + w_c + w_n
            sm.append([(w_p * disp[i - 1][k] + w_c * disp[i][k] + w_n * disp[(i + 1) % n][k]) / tot for k in (0, 1)])
        disp = sm
    keep_direction()
    out = [[P[i][0] + disp[i][0], P[i][1] + disp[i][1], c[i][2]] for i in range(n)]
    return out


def _loops(c):
    """Whether integer contour c crosses itself (pathops finds a different outline after simplifying)."""
    p = pathops.Path()
    pen = p.getPen()
    n = len(c)
    k = next(i for i, q in enumerate(c) if q[2])
    pts = c[k:] + c[:k]
    pen.moveTo(pts[0][:2])
    offs = []
    for q in pts[1:] + [pts[0]]:
        if q[2]:
            if offs:
                pen.qCurveTo(*offs, q[:2])
            else:
                pen.lineTo(q[:2])
            offs = []
        else:
            offs.append(q[:2])
    if offs:
        pen.qCurveTo(*offs, pts[0][:2])
    pen.closePath()
    q = pathops.Path()
    p.draw(q.getPen())
    q.simplify(fix_winding=True)
    return len(list(q.contours)) != 1 or abs(abs(p.area) - abs(q.area)) > 0.5


def _side(c, t):
    """Which way contour c turns at point t (+1 left, -1 right, 0 straight)."""
    n = len(c)
    a, p, b = c[t - 1], c[t], c[(t + 1) % n]
    z = (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])
    return (z > 0) - (z < 0)


def _restore_tangents(out, c):
    """Make the moved contour `out` (lists, edited in place) as smooth or as cornered as master `c`."""
    n = len(c)
    # points that are smooth in the master (tangent turn under 3 degrees) are smooth again
    for i in range(n):
        if not c[i][2]:
            continue
        ia, ib = (i - 1) % n, (i + 1) % n
        if c[ia][2] and c[ib][2]:
            continue
        mt = _turn_deg(c[ia], c[i], c[ib])
        if mt >= 30.0:
            # a corner next to a curve stays a corner: the handle keeps the master's turn
            a, p, b = out[ia], out[i], out[ib]
            if 3.0 < _turn_deg(a, p, b) < 30.0:
                ma, mp, mb = c[ia], c[i], c[ib]
                if c[ib][2]:  # rotate the incoming handle a
                    ang = math.atan2(mb[1] - mp[1], mb[0] - mp[0]) - math.atan2(mp[1] - ma[1], mp[0] - ma[0])
                    base = math.atan2(b[1] - p[1], b[0] - p[0]) - ang
                    lh = math.hypot(p[0] - a[0], p[1] - a[1])
                    a[0], a[1] = p[0] - lh * math.cos(base), p[1] - lh * math.sin(base)
                else:         # rotate the outgoing handle b
                    ang = math.atan2(mb[1] - mp[1], mb[0] - mp[0]) - math.atan2(mp[1] - ma[1], mp[0] - ma[0])
                    base = math.atan2(p[1] - a[1], p[0] - a[0]) + ang
                    lh = math.hypot(b[0] - p[0], b[1] - p[1])
                    b[0], b[1] = p[0] + lh * math.cos(base), p[1] + lh * math.sin(base)
            continue
        if mt >= 3.0:
            continue
        a, p, b = out[ia], out[i], out[ib]
        if not c[ia][2] and not c[ib][2]:
            ex, ey = b[0] - a[0], b[1] - a[1]
            L2 = ex * ex + ey * ey
            if L2 > 1e-9:
                r = max(0.15, min(0.85, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / L2))
                p[0], p[1] = a[0] + r * ex, a[1] + r * ey
        else:
            o, h = (a, b) if c[ia][2] else (b, a)
            dx, dy = p[0] - o[0], p[1] - o[1]
            L = math.hypot(dx, dy)
            lh = math.hypot(h[0] - p[0], h[1] - p[1])
            if L > 1e-9:
                h[0], h[1] = p[0] + dx / L * lh, p[1] + dy / L * lh
    # a master corner whose turn the steps above left between 3 and 30 degrees (it would read as a
    # kink), or folded 50 degrees sharper than the master and past 110 (a spike), moves its own
    # point a few units until neither holds (aiming at 34 degrees, so rounding cannot bring it under 30)
    def kinks(j):
        bad = 0
        for t in (j - 1, j, j + 1):
            t %= n
            if not out[t][2]:
                continue
            tn = _turn_deg(out[t - 1], out[t], out[(t + 1) % n])
            if _turn_deg(c[t - 1], c[t], c[(t + 1) % n]) > 10.0 and _side(out, t) != _side(c, t):
                bad += 1  # turns the other way: a fold or a loop
                continue
            if tn > max(110.0, _turn_deg(c[t - 1], c[t], c[(t + 1) % n]) + 50.0):
                bad += 1  # folded into a spike
                continue
            if out[t - 1][2] and out[(t + 1) % n][2]:
                continue
            if 3.0 < _turn_deg(out[t - 1], out[t], out[(t + 1) % n]) < 34.0 and _turn_deg(c[t - 1], c[t], c[(t + 1) % n]) >= 30.0:
                bad += 1
            elif 3.0 < _turn_deg(out[t - 1], out[t], out[(t + 1) % n]) < 30.0:
                bad += 1
        return bad
    for i in range(n):
        if not c[i][2] or _turn_deg(c[i - 1], c[i], c[(i + 1) % n]) < 30.0:
            continue
        if kinks(i) == 0:
            continue
        x0, y0 = out[i][0], out[i][1]
        best = None
        for r in range(1, 15):
            for k in range(16):
                ang = 2 * math.pi * k / 16
                out[i][0], out[i][1] = x0 + r * math.cos(ang), y0 + r * math.sin(ang)
                if kinks(i) == 0:
                    best = (out[i][0], out[i][1])
                    break
            if best:
                break
        out[i][0], out[i][1] = best if best else (x0, y0)
    return [tuple(q) for q in out]


def _polish(c, intersect=True):
    """The integer polish of one contour (edited in place): handles between two straight runs go to
    their lines' intersection (unless intersect is false), then kinks are straightened."""
    n = len(c)
    if intersect:
            for i in range(n):
                p0, p1, h, p2, p3 = c[i - 2], c[i - 1], c[i], c[(i + 1) % n], c[(i + 2) % n]
                if p0[2] and p1[2] and (not h[2]) and p2[2] and p3[2]:
                    if _turn_deg(p0, p1, h) < 30.0 and _turn_deg(h, p2, p3) < 30.0:
                        d1x, d1y = p1[0] - p0[0], p1[1] - p0[1]
                        d2x, d2y = p2[0] - p3[0], p2[1] - p3[1]
                        den = d1x * d2y - d1y * d2x
                        if abs(den) > 1e-6:
                            t1 = ((p2[0] - p1[0]) * d2y - (p2[1] - p1[1]) * d2x) / den
                            t2 = ((p1[0] - p2[0]) * d1y - (p1[1] - p2[1]) * d1x) / (-den)
                            if 3.0 < t1 * math.hypot(d1x, d1y) < 120.0 and 3.0 < t2 * math.hypot(d2x, d2y) < 120.0:
                                ix, iy = p1[0] + t1 * d1x, p1[1] + t1 * d1y
                                cands = [(round(ix) + dx, round(iy) + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)]
                                best_h = min(cands, key=lambda q: (max(_turn_deg(p0, p1, q), _turn_deg(q, p2, p3)), math.hypot(q[0] - ix, q[1] - iy)))
                                if max(_turn_deg(p0, p1, best_h), _turn_deg(best_h, p2, p3)) <= 2.5:
                                    c[i] = (best_h[0], best_h[1], False)

    for _ in range(6):
        moved = False
        for i in range(n):
            a, p, b = c[i - 1], c[i], c[(i + 1) % n]
            if not p[2] or (a[2] and b[2]):
                continue
            t = _turn_deg(a, p, b)
            if not (0.35 < t < 30.0):
                continue
            if not a[2] and not b[2]:
                ax, ay = a[0], a[1]
                bx, by = b[0], b[1]
                L2 = (bx - ax) ** 2 + (by - ay) ** 2
                if L2 == 0:
                    continue
                r = max(0.22, min(0.78, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / L2))
                ix, iy = ax + r * (bx - ax), ay + r * (by - ay)
                cands = [(round(ix) + dx, round(iy) + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)]
                cands = [q for q in cands if math.hypot(q[0] - a[0], q[1] - a[1]) >= 2.5 and math.hypot(q[0] - b[0], q[1] - b[1]) >= 2.5]
                if cands:
                    best_q = min(cands, key=lambda q: (round(_turn_deg(a, q, b), 2), math.hypot(q[0] - p[0], q[1] - p[1])))
                    if _turn_deg(a, best_q, b) < t and best_q != p[:2]:
                        c[i] = (best_q[0], best_q[1], True)
                        moved = True
            elif a[2]:
                dx, dy = p[0] - a[0], p[1] - a[1]
                L = math.hypot(dx, dy)
                Lh = math.hypot(b[0] - p[0], b[1] - p[1])
                if L == 0:
                    continue
                nxt = c[(i + 2) % n]
                cands = []
                for s in (Lh, Lh + 1.0, max(3.5, Lh - 1.0), Lh + 2.5):
                    ix, iy = p[0] + dx / L * s, p[1] + dy / L * s
                    for ox in (-2, -1, 0, 1, 2):
                        for oy in (-2, -1, 0, 1, 2):
                            q = (round(ix) + ox, round(iy) + oy)
                            if math.hypot(q[0] - p[0], q[1] - p[1]) >= 2.5 and math.hypot(q[0] - nxt[0], q[1] - nxt[1]) >= 2.5:
                                cands.append(q)
                if cands:
                    best_q = min(cands, key=lambda q: (round(_turn_deg(a, p, q), 2), math.hypot(q[0] - b[0], q[1] - b[1])))
                    if _turn_deg(a, p, best_q) < t and best_q != b[:2]:
                        if not (nxt[2] and _turn_deg(b, nxt, c[(i + 3) % n]) < 30.0 and _turn_deg(best_q, nxt, c[(i + 3) % n]) > 2.6):
                            c[(i + 1) % n] = (best_q[0], best_q[1], False)
                            moved = True
            else:
                dx, dy = b[0] - p[0], b[1] - p[1]
                L = math.hypot(dx, dy)
                Lh = math.hypot(a[0] - p[0], a[1] - p[1])
                if L == 0:
                    continue
                prv = c[i - 2]
                cands = []
                for s in (Lh, Lh + 1.0, max(3.5, Lh - 1.0), Lh + 2.5):
                    ix, iy = p[0] - dx / L * s, p[1] - dy / L * s
                    for ox in (-2, -1, 0, 1, 2):
                        for oy in (-2, -1, 0, 1, 2):
                            q = (round(ix) + ox, round(iy) + oy)
                            if math.hypot(q[0] - p[0], q[1] - p[1]) >= 2.5 and math.hypot(q[0] - prv[0], q[1] - prv[1]) >= 2.5:
                                cands.append(q)
                if cands:
                    best_q = min(cands, key=lambda q: (round(_turn_deg(q, p, b), 2), math.hypot(q[0] - a[0], q[1] - a[1])))
                    if _turn_deg(best_q, p, b) < t and best_q != a[:2]:
                        if not (prv[2] and _turn_deg(c[i - 3], prv, a) < 30.0 and _turn_deg(c[i - 3], prv, best_q) > 2.6):
                            c[i - 1] = (best_q[0], best_q[1], False)
                            moved = True
        if not moved:
            break

    for _ in range(12):
        cur_bad = _contour_defects(c)
        if not cur_bad:
            break
        fixed_one = False
        for i in range(n):
            a, p, b = c[i - 1], c[i], c[(i + 1) % n]
            if not p[2] or (a[2] and b[2]):
                continue
            t = _turn_deg(a, p, b)
            if not (2.8 < t < 30.0):
                continue
            best_cand = None
            best_cost = 9999.0
            da_rng = (-2, -1, 0, 1, 2) if not a[2] else (0,)
            db_rng = (-2, -1, 0, 1, 2) if not b[2] else (0,)
            for dpx in (-1, 0, 1):
                for dpy in (-1, 0, 1):
                    np = (p[0] + dpx, p[1] + dpy, True)
                    for dax in da_rng:
                        for day in da_rng:
                            na = (a[0] + dax, a[1] + day, a[2])
                            for dbx in db_rng:
                                for dby in db_rng:
                                    nb = (b[0] + dbx, b[1] + dby, b[2])
                                    ang = _turn_deg(na, np, nb)
                                    if ang > 2.4:
                                        continue
                                    cost = (0.0 if ang <= 0.30 else 10.0 + ang) + 2.5 * (abs(dpx) + abs(dpy)) + (abs(dax) + abs(day) + abs(dbx) + abs(dby))
                                    if cost >= best_cost:
                                        continue
                                    old_a, old_p, old_b = c[i - 1], c[i], c[(i + 1) % n]
                                    c[i - 1], c[i], c[(i + 1) % n] = na, np, nb
                                    nbad = _contour_defects(c)
                                    c[i - 1], c[i], c[(i + 1) % n] = old_a, old_p, old_b
                                    if len(nbad) < len(cur_bad):
                                        best_cost = cost
                                        best_cand = (na, np, nb)
            if best_cand is not None:
                c[i - 1], c[i], c[(i + 1) % n] = best_cand
                fixed_one = True
                break
        if not fixed_one:
            break


def _modulate_and_polish(contours, fields, lsb, rsb, sv, sb_knob, bold_knob, cp=None):
    sb_ratio = sb_knob / 1.22
    if abs(sv - 1.0) < 1e-6:
        sx = 1.0
        out_contours = [[(x, y, on) for x, y, on in c] for c in contours]
    else:
        _r, sx, d = _weight_params(sv, bold_knob)
        hair = _HAIR_BY_CP.get(cp, _HAIR)
        if d > 0 and cp in _GAIN_BY_CP:
            d *= _GAIN_BY_CP[cp] / _GAIN
        out_contours = [_displace(c, cf, sx, d, hair) for c, cf in zip(contours, fields)]
        # strokes grow inward at the top and bottom, as the Latin's do: the glyph keeps the master's
        # vertical extent (baseline, x-height, cap height, ascender and descender)
        y0 = min(p[1] for c in contours for p in c)
        y1 = max(p[1] for c in contours for p in c)
        n0 = min(p[1] for c in out_contours for p in c)
        n1 = max(p[1] for c in out_contours for p in c)
        if d > 0 and n1 - n0 > 1e-6:
            # the middle of the glyph keeps its place; the top and bottom bands (_BAND of the height
            # each) take the growth back, so the extremes return to the master's
            ya, yb = y0 + _BAND * (y1 - y0), y1 - _BAND * (y1 - y0)
            def ymap(y):
                if y < ya:
                    return ya - (ya - y) * (ya - y0) / max(1e-6, ya - n0)
                if y > yb:
                    return yb + (y - yb) * (y1 - yb) / max(1e-6, n1 - yb)
                return y
            out_contours = [[[x, ymap(y), on] for x, y, on in c] for c in out_contours]
        out_contours = [_restore_tangents(oc, c) for oc, c in zip(out_contours, contours)]

    xmin = min(p[0] for c in out_contours for p in c)
    xmax = max(p[0] for c in out_contours for p in c)
    sb_scale = sb_ratio * (1.0 + 0.04 * (sx - 1.0))
    lsb_w = round(lsb * sb_scale)
    rsb_w = round(rsb * sb_scale)
    c_int = [[(round(x - xmin + lsb_w), round(y), on) for x, y, on in c] for c in out_contours]
    adv_w = round((xmax - xmin) + lsb_w + rsb_w)

    c_pre = [list(c) for c in c_int]
    for c in c_int:
        _polish(c)
    # the polish may pull a handle across a sharp corner into a sliver loop; then the polished moves
    # are undone one at a time (the one that leaves the fewest problems first) until the loop is gone
    for k, c in enumerate(c_int):
        while _loops(c):
            moved = [i for i in range(len(c)) if c[i] != c_pre[k][i]]
            if not moved:
                break
            def cost(i):
                trial = list(c)
                trial[i] = c_pre[k][i]
                return (_loops(trial), len(_contour_defects(trial)))
            best = min(moved, key=cost)
            c[best] = c_pre[k][best]
    g = Glyph()
    g.numberOfContours = len(c_int)
    g.coordinates = GlyphCoordinates([(x, y) for c in c_int for x, y, _ in c])
    g.flags = array('B', [1 if on else 0 for c in c_int for _, _, on in c])
    ends = []
    k = -1
    for c in c_int:
        k += len(c)
        ends.append(k)
    g.endPtsOfContours = ends
    return g, adv_w


def _ensure_format12(font):
    """Ensure both (3, 10) and (0, 4) format 12 Unicode subtables exist and hold all best-cmap entries."""
    cmap = font['cmap']
    best = dict(font.getBestCmap())
    added = False
    for plat, enc in ((3, 10), (0, 4)):
        existing = next((t for t in cmap.tables if t.platformID == plat and t.platEncID == enc and t.format == 12), None)
        if existing is None:
            t = cmap_format_12(12)
            t.platformID = plat
            t.platEncID = enc
            t.language = 0
            t.cmap = dict(best)
            cmap.tables.append(t)
            added = True
        else:
            for u, g in best.items():
                existing.cmap.setdefault(u, g)
    return added


def glyphs(ctx):
    font, glyf, hmtx = ctx.font, ctx.glyf, ctx.hmtx
    order = set(font.getGlyphOrder())
    cmap = font.getBestCmap()
    sb_knob = ctx.P('FRAK_SB', 1.22)
    bold_knob = ctx.P('FRAK_BOLD', 1.0)

    if _ensure_format12(font):
        ctx.log('cmap: format 12 subtables (3,10) and (0,4) added, copies of the best cmap')

    masters = _unpack_masters()
    upright_store = ctx._fraktur_upright = {}
    new_names = []
    k_it, yc_it = ctx.ITALIC_K, ctx.ITALIC_YC

    for cp, _ch, _is_uc, cs, fields, lsb, rsb in masters:
        name = f'u{cp:04X}' if cp > 0xFFFF else f'uni{cp:04X}'
        assert name not in order, f'fraktur: glyph {name} already exists'
        assert cp not in cmap, f'fraktur: U+{cp:04X} already mapped to {cmap[cp]}'
        g_up, adv = _modulate_and_polish(cs, fields, lsb, rsb, ctx.SV, sb_knob, bold_knob, cp)
        g_up.program = ctx.EMPTY_PROGRAM()
        g_up.recalcBounds(glyf)
        upright_store[name] = (g_up, adv)

        if ctx.ITALIC and k_it:
            g_work = copy.deepcopy(g_up)
            g_work.coordinates = GlyphCoordinates([(x - k_it * (y - yc_it), y) for x, y in g_up.coordinates])
            g_work.recalcBounds(glyf)
            glyf[name] = g_work
            hmtx[name] = (adv, g_work.xMin)
        else:
            glyf[name] = copy.deepcopy(g_up)
            hmtx[name] = (adv, g_up.xMin)

        if name not in font.getGlyphOrder():
            font.setGlyphOrder(font.getGlyphOrder() + [name])
        new_names.append(name)
        ctx.GDEF_CLASS[name] = 1

    for (cp, *_), name in zip(masters, new_names):
        ctx.map(cp, name)

    ctx.log(f'{len(new_names)} Mathematical Fraktur glyphs (SV={ctx.SV:.3f}, FRAK_SB={sb_knob:g}, FRAK_BOLD={bold_knob:g})')


def post(ctx):
    """Restore exact polished upright outlines before meta's ttfautohint and verify format 12 cmap."""
    font, glyf, hmtx = ctx.font, ctx.glyf, ctx.hmtx
    upright_store = getattr(ctx, '_fraktur_upright', None) or {}
    for name, (g_up, adv) in upright_store.items():
        g_clean = copy.deepcopy(g_up)
        g_clean.program = ctx.EMPTY_PROGRAM()
        g_clean.recalcBounds(glyf)
        glyf[name] = g_clean
        hmtx[name] = (adv, g_clean.xMin)

    tables = {(t.platformID, t.platEncID, t.format): t for t in font['cmap'].tables}
    t4 = tables.get((3, 1, 4))
    for key in ((3, 10, 12), (0, 4, 12)):
        t12 = tables.get(key)
        if t12 is None:
            raise SystemExit(f'fraktur: missing cmap subtable {key}')
        if t4 is not None:
            bad = [u for u, g in t4.cmap.items() if t12.cmap.get(u) != g]
            if bad:
                raise SystemExit(f'fraktur: cmap {key} disagrees with (3,1,4) at {[hex(u) for u in bad[:8]]}')
