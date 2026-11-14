# Componenti di terze parti

Il codice originale di Fuorigiri è GPL-3.0-or-later. Le dipendenze mantengono le proprie licenze e i relativi avvisi.

Principali componenti: Python, FastAPI, Uvicorn, Pydantic, NumPy, Matplotlib, ReportLab, fitdecode, cryptography, React, TypeScript, Vite, Plotly.js, Lucide, PySide6/Qt e PyInstaller.

fitdecode: MIT, https://github.com/polyvertex/fitdecode/blob/master/LICENSE.txt. Lo SDK Garmin non è una dipendenza del progetto.

PySide6/Qt e Qt WebEngine includono condizioni e componenti di terzi: conservare gli avvisi e fornire le modalità richieste per accedere ai relativi sorgenti. Il pacchetto di sviluppo non è un installer firmato né una release pubblica pronta alla distribuzione. Prima di pubblicarlo completare l'inventario delle licenze, includere i testi delle dipendenze e gli adempimenti relativi a Qt/Chromium.

Le versioni risolte sono registrate in `requirements-lock-windows.txt` e `frontend/package-lock.json`. Il lock Python Windows è un riferimento della macchina di verifica, non un lock portabile a Linux (contiene dipendenze specifiche del sistema).
# Marchio e logo della società

`frontend/public/branding/progetto-ciclismo.png` è il logo fornito da Luca Bontempi per l'inclusione nel software sviluppato per Progetto Ciclismo - Rodengo Saiano A.S.D. Il marchio è distinto dal codice GPL; la distribuzione del sorgente non concede automaticamente diritti ulteriori sul marchio. L'asset originale è conservato senza modifiche e incluso localmente nel bundle e nei report.


## Aggiunte 0.6

Keyring 25.7.0 e relative dipendenze: conservare licenze/metadati delle wheel nel pacchetto; Windows Credential Manager e Linux Secret Service. Android: Kotlin, AndroidX Activity/WebKit/WorkManager, Chaquopy e runtime Python, più le dipendenze native scientifiche/critto elencate in android/requirements.txt. La matrice nativa e la raccolta completa degli avvisi devono essere verificate sul builder Android prima di distribuire un APK.

Inno Setup è uno strumento di build con propria licenza, non una dipendenza da installare sul PC destinatario. Flatpak e i runtime mantengono le proprie licenze. Le pipeline e i checksum non costituiscono una firma del prodotto o un audit legale completo.

La nuova icona Fuorigiri (`fuorigiri.svg` e derivate) è opera del progetto e segue GPL-3.0-or-later. Il logo societario originale e la sua attribuzione rimangono invariati.

Android incorpora il client Google Play services Auth 22.0.0 tramite Gradle. Prima di distribuire l’APK occorre verificare i termini della libreria client, le dipendenze transitive e la compatibilità della loro redistribuzione con la GPL applicata all’app. Il POM della versione 22.0.0 dichiara Android Software Development Kit License. [POM ufficiale](https://dl.google.com/dl/android/maven2/com/google/android/gms/play-services-auth/22.0.0/play-services-auth-22.0.0.pom) · [Condizioni Android SDK](https://developer.android.com/studio/terms)

## Distribuzione del codice e dei binari

GPL-3.0-or-later esprime la scelta per il codice originale anche quando la repository diventa pubblica. Per un download dei binari offrire accesso equivalente al sorgente corrispondente, alle modifiche, agli script di compilazione e installazione e ai componenti richiesti. Conservare avvisi e condizioni delle dipendenze. I soli hash delle wheel e il lockfile identificano versioni ma non forniscono i sorgenti. [GPLv3, sezioni 1 e 6](https://www.gnu.org/licenses/gpl-3.0.html)

**13 novembre 2026 — avvisi Qt nel bundle Windows:** `packaging/licenses/qt/` contiene LGPL v3 e v2.1, la nota sui sorgenti corrispondenti e la sostituibilità delle librerie (`LEGGIMI-QT.txt`), più gli avvisi Chromium di Qt WebEngine 6.140.0: 126 componenti, tutti con testo. I testi provengono dall’archivio sorgente ufficiale e, per 10 componenti, dalle pagine di licenza Qt della stessa versione; provenienza e digest sono in `PROVENIENZA.json`. `scripts/build.py` li copia in `licenses/qt` e interrompe la build se PySide6, Qt, WebEngine o Chromium installati non corrispondono. Resta la scelta di come garantire l’accesso ai sorgenti Qt: link agli archivi ufficiali o copia allegata alla release.

Su Windows i metadati locali di PySide6/Shiboken 6.12.0 indicano LGPL-3.0-only, GPL-2.0-only o GPL-3.0-only. Le cartelle licenses delle wheel ispezionate contengono soltanto LicenseRef-Qt-Commercial.txt. Per la distribuzione open source completare testi applicabili, avvisi Chromium e accesso ai sorgenti delle esatte versioni WebEngine/PySide/Qt distribuite. Il runtime rileva Qt 6.12.0, WebEngine 6.140.0 e Chromium 140.0.7339.225. [Sorgenti Qt 6.12.0](https://download.qt.io/archive/qt/6.12/6.12.0/submodules/) · [Sorgenti PySide 6.12.0](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/) · [Avvisi dei componenti](https://doc.qt.io/qt-6/licenses-used-in-qt.html) · [Obblighi Qt](https://www.qt.io/development/open-source-lgpl-obligations)

## Libreria UI della suite

`@cycling-suite/ui` 0.2.9: codice GPL-3.0-or-later estratto dalla repository autonoma cycling-suite-common. Artefatto versionato, sorgenti TypeScript e script di build, licenza e NOTICE inclusi in frontend/vendor; commit/tag e checksum in suite-ui-provenance.json. React rimane una peer dependency fornita da Fuorigiri. Il logo societario è identico all’originale e mantiene le condizioni del marchio sopra indicate.

## Pillow Android 13.0.0 e librerie statiche

Pillow: MIT-CMU, testo incluso nella wheel. Le wheel Android API 26 incorporano libjpeg-turbo 3.2.0 e FreeType 2.14.3 (scelta FreeType License, FTL). Sorgenti, commit, checksum e verifiche in android/wheels/PILLOW_BUILD.json. Zlib è una dipendenza del sistema Android.

This software is based in part on the work of the Independent JPEG Group.

This software is based in part on the work of the FreeType Team. https://freetype.org

Testi originali dai sorgenti utilizzati:

### jpeg — LICENSE.md

```text
libjpeg-turbo Licenses
======================

libjpeg-turbo is covered by two compatible BSD-style open source licenses:

- The IJG (Independent JPEG Group) License, which is listed in
  [README.ijg](README.ijg)

  This license applies to the libjpeg API library and associated programs,
  including any code inherited from libjpeg and any modifications to that
  code.

- The Modified (3-clause) BSD License, which is listed below

  This license applies to the TurboJPEG API library and associated programs,
  [libspng](https://libspng.org) (which is used by cjpeg and djpeg), and the
  build/test system.

  * The TurboJPEG API library wraps the libjpeg API library, so in the context
    of the overall TurboJPEG API library, both the terms of the IJG License and
    the terms of the Modified (3-clause) BSD License apply.
  * cjpeg and djpeg use libspng, so in the context of those programs, both the
    terms of the IJG License and the terms of the Modified (3-clause) BSD
    License apply.


Component Licenses
==================

Some of libjpeg-turbo's modules and internal dependencies are covered by less
restrictive licenses, but in the context of libjpeg-turbo as a whole, the terms
of the less restrictive licenses are subsumed by either the IJG License or the
Modified BSD License.  (In other words, the terms of the less restrictive
licenses are satisfied if the terms of the IJG and Modified BSD Licenses are
satisfied.)

- The libjpeg-turbo SIMD source code and zlib are covered by the
  [zlib License](https://spdx.org/licenses/Zlib.html), which is subsumed by the
  IJG License in the context of the cjpeg and djpeg programs and the libjpeg
  API library.

- Some of the libspng source code is covered by the
  [PNG Reference Library License v2](https://spdx.org/licenses/libpng-2.0.html),
  which is subsumed by the IJG License in the context of the cjpeg and djpeg
  programs and the TurboJPEG API library.

- Most of the libspng source code is covered by the
  [Simplified (2-clause) BSD License](https://spdx.org/licenses/BSD-2-Clause.html),
  which is subsumed by the Modified BSD License in the context of the cjpeg and
  djpeg programs and the TurboJPEG API library.


Complying with the libjpeg-turbo Licenses
=========================================

This section provides a roll-up of the libjpeg-turbo licensing terms, to the
best of our understanding.  This is not a license in and of itself.  It is
intended solely for clarification.

1.  If you are distributing a modified version of the libjpeg-turbo source,
    then:

    1.  You cannot alter or remove any existing copyright or license notices
        from the source.

        **Origin**
        - Clause 1 of the IJG License
        - Clause 1 of the Modified BSD License

    2.  You must add your own copyright notice to the header of each source
        file you modified, so others can tell that you modified that file.  (If
        there is not an existing copyright header in that file, then you can
        simply add a notice stating that you modified the file.)

        **Origin**
        - Clause 1 of the IJG License

    3.  You must include the IJG README file, and you must not alter any of the
        copyright or license text in that file.

        **Origin**
        - Clause 1 of the IJG License

2.  If you are distributing only libjpeg-turbo binaries without the source, or
    if you are distributing an application that statically links with
    libjpeg-turbo, then:

    1.  Your product documentation must include a message stating:

        This software is based in part on the work of the Independent JPEG
        Group.

        **Origin**
        - Clause 2 of the IJG license

    2.  If your binary distribution includes or uses the TurboJPEG API or
        associated programs, cjpeg, or djpeg, then your product documentation
        must include the text of the Modified BSD License (see below.)

        **Origin**
        - Clause 2 of the Modified BSD License

3.  You cannot use the name of the IJG or The libjpeg-turbo Project or the
    contributors thereof in advertising, publicity, etc.

    **Origin**
    - IJG License
    - Clause 3 of the Modified BSD License

4.  The authors and distributors do not warrant libjpeg-turbo to be free of
    defects, nor do we accept any liability for undesirable consequences
    resulting from your use of the software.

    **Origin**
    - IJG License
    - Modified BSD License


The Modified (3-clause) BSD License
===================================

Copyright (C) 2009-2026 D. R. Commander<br>
Copyright (C) 2018-2023 Randy <randy408@protonmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the libjpeg-turbo Project nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS",
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

```

### jpeg — README.ijg

```text
libjpeg-turbo note:  This file has been modified by The libjpeg-turbo Project
to include only information relevant to libjpeg-turbo, to wordsmith certain
sections, and to remove impolitic language that existed in the libjpeg v8
README.  It is included only for reference.  Please see README.md for
information specific to libjpeg-turbo.


The Independent JPEG Group's JPEG software
==========================================

This distribution contains a release of the Independent JPEG Group's free JPEG
software.  You are welcome to redistribute this software and to use it for any
purpose, subject to the conditions under LEGAL ISSUES, below.

This software is the work of Tom Lane, Guido Vollbeding, Philip Gladstone,
Bill Allombert, Jim Boucher, Lee Crocker, Bob Friesenhahn, Ben Jackson,
Julian Minguillon, Luis Ortiz, George Phillips, Davide Rossi, Ge' Weijers,
and other members of the Independent JPEG Group.

IJG is not affiliated with the ISO/IEC JTC1/SC29/WG1 standards committee
(also known as JPEG, together with ITU-T SG16).


DOCUMENTATION ROADMAP
=====================

This file contains the following sections:

OVERVIEW            General description of JPEG and the IJG software.
LEGAL ISSUES        Copyright, lack of warranty, terms of distribution.
REFERENCES          Where to learn more about JPEG.
ARCHIVE LOCATIONS   Where to find newer versions of this software.
FILE FORMAT WARS    Software *not* to get.
TO DO               Plans for future IJG releases.

Other documentation files in the distribution are:

User documentation:
  doc/usage.txt         Usage instructions for cjpeg, djpeg, jpegtran,
                        rdjpgcom, and wrjpgcom.
  doc/*.1               Unix-style man pages for programs (same info as
                        usage.txt).
  doc/wizard.txt        Advanced usage instructions for JPEG wizards only.
  doc/change.log        Version-to-version change highlights.
Programmer and internal documentation:
  doc/libjpeg.txt       How to use the JPEG library in your own programs.
  src/example.c         Sample code for calling the JPEG library.
  doc/structure.txt     Overview of the JPEG library's internal structure.
  doc/coderules.txt     Coding style rules --- please read if you contribute
                        code.

Please read at least usage.txt.  Some information can also be found in the JPEG
FAQ (Frequently Asked Questions) article.  See ARCHIVE LOCATIONS below to find
out where to obtain the FAQ article.

If you want to understand how the JPEG code works, we suggest reading one or
more of the REFERENCES, then looking at the documentation files (in roughly
the order listed) before diving into the code.


OVERVIEW
========

This package contains C software to implement JPEG image encoding, decoding,
and transcoding.  JPEG (pronounced "jay-peg") is a standardized compression
method for full-color and grayscale images.  JPEG's strong suit is compressing
photographic images or other types of images that have smooth color and
brightness transitions between neighboring pixels.  Images with sharp lines or
other abrupt features may not compress well with JPEG, and a higher JPEG
quality may have to be used to avoid visible compression artifacts with such
images.

JPEG is normally lossy, meaning that the output pixels are not necessarily
identical to the input pixels.  However, on photographic content and other
"smooth" images, very good compression ratios can be obtained with no visible
compression artifacts, and extremely high compression ratios are possible if
you are willing to sacrifice image quality (by reducing the "quality" setting
in the compressor.)

This software implements JPEG baseline, extended-sequential, progressive, and
lossless compression processes.  Provision is made for supporting all variants
of these processes, although some uncommon parameter settings aren't
implemented yet.  We have made no provision for supporting the hierarchical
processes defined in the standard.

We provide a set of library routines for reading and writing JPEG image files,
plus two sample applications "cjpeg" and "djpeg", which use the library to
perform conversion between JPEG and some other popular image file formats.
The library is intended to be reused in other applications.

In order to support file conversion and viewing software, we have included
considerable functionality beyond the bare JPEG coding/decoding capability;
for example, the color quantization modules are not strictly part of JPEG
decoding, but they are essential for output to colormapped file formats.  These
extra functions can be compiled out of the library if not required for a
particular application.

We have also included "jpegtran", a utility for lossless transcoding between
different JPEG processes, and "rdjpgcom" and "wrjpgcom", two simple
applications for inserting and extracting textual comments in JFIF files.

The emphasis in designing this software has been on achieving portability and
flexibility, while also making it fast enough to be useful.  In particular,
the software is not intended to be read as a tutorial on JPEG.  (See the
REFERENCES section for introductory material.)  Rather, it is intended to
be reliable, portable, industrial-strength code.  We do not claim to have
achieved that goal in every aspect of the software, but we strive for it.

We welcome the use of this software as a component of commercial products.
No royalty is required, but we do ask for an acknowledgement in product
documentation, as described under LEGAL ISSUES.


LEGAL ISSUES
============

In plain English:

1. We don't promise that this software works.  (But if you find any bugs,
   please let us know!)
2. You can use this software for whatever you want.  You don't have to pay us.
3. You may not pretend that you wrote this software.  If you use it in a
   program, you must acknowledge somewhere in your documentation that
   you've used the IJG code.

In legalese:

The authors make NO WARRANTY or representation, either express or implied,
with respect to this software, its quality, accuracy, merchantability, or
fitness for a particular purpose.  This software is provided "AS IS", and you,
its user, assume the entire risk as to its quality and accuracy.

This software is copyright (C) 1991-2020, Thomas G. Lane, Guido Vollbeding.
All Rights Reserved except as specified below.

Permission is hereby granted to use, copy, modify, and distribute this
software (or portions thereof) for any purpose, without fee, subject to these
conditions:
(1) If any part of the source code for this software is distributed, then this
README file must be included, with this copyright and no-warranty notice
unaltered; and any additions, deletions, or changes to the original files
must be clearly indicated in accompanying documentation.
(2) If only executable code is distributed, then the accompanying
documentation must state that "this software is based in part on the work of
the Independent JPEG Group".
(3) Permission for use of this software is granted only if the user accepts
full responsibility for any undesirable consequences; the authors accept
NO LIABILITY for damages of any kind.

These conditions apply to any software derived from or based on the IJG code,
not just to the unmodified library.  If you use our work, you ought to
acknowledge us.

Permission is NOT granted for the use of any IJG author's name or company name
in advertising or publicity relating to this software or products derived from
it.  This software may be referred to only as "the Independent JPEG Group's
software".

We specifically permit and encourage the use of this software as the basis of
commercial products, provided that all warranty or liability claims are
assumed by the product vendor.


REFERENCES
==========

We recommend reading one or more of these references before trying to
understand the innards of the JPEG software.

The best short technical introduction to the JPEG compression algorithm is
        Wallace, Gregory K.  "The JPEG Still Picture Compression Standard",
        Communications of the ACM, April 1991 (vol. 34 no. 4), pp. 30-44.
(Adjacent articles in that issue discuss MPEG motion picture compression,
applications of JPEG, and related topics.)  If you don't have the CACM issue
handy, a PDF file containing a revised version of Wallace's article is
available at http://www.ijg.org/files/Wallace.JPEG.pdf.  The file (actually
a preprint for an article that appeared in IEEE Trans. Consumer Electronics)
omits the sample images that appeared in CACM, but it includes corrections
and some added material.  Note: the Wallace article is copyright ACM and IEEE,
and it may not be used for commercial purposes.

A somewhat less technical, more leisurely introduction to JPEG can be found in
"The Data Compression Book" by Mark Nelson and Jean-loup Gailly, published by
M&T Books (New York), 2nd ed. 1996, ISBN 1-55851-434-1.  This book provides
good explanations and example C code for a multitude of compression methods
including JPEG.  It is an excellent source if you are comfortable reading C
code but don't know much about data compression in general.  The book's JPEG
sample code is far from industrial-strength, but when you are ready to look
at a full implementation, you've got one here...

The best currently available description of JPEG is the textbook "JPEG Still
Image Data Compression Standard" by William B. Pennebaker and Joan L.
Mitchell, published by Van Nostrand Reinhold, 1993, ISBN 0-442-01272-1.
Price US$59.95, 638 pp.  The book includes the complete text of the ISO JPEG
standards (DIS 10918-1 and draft DIS 10918-2).

The original JPEG standard is divided into two parts, Part 1 being the actual
specification, while Part 2 covers compliance testing methods.  Part 1 is
titled "Digital Compression and Coding of Continuous-tone Still Images,
Part 1: Requirements and guidelines" and has document numbers ISO/IEC IS
10918-1, ITU-T T.81.  Part 2 is titled "Digital Compression and Coding of
Continuous-tone Still Images, Part 2: Compliance testing" and has document
numbers ISO/IEC IS 10918-2, ITU-T T.83.

The JPEG standard does not specify all details of an interchangeable file
format.  For the omitted details, we follow the "JFIF" conventions, revision
1.02.  JFIF version 1 has been adopted as ISO/IEC 10918-5 (05/2013) and
Recommendation ITU-T T.871 (05/2011): Information technology - Digital
compression and coding of continuous-tone still images: JPEG File Interchange
Format (JFIF).  It is available as a free download in PDF file format from
https://www.iso.org/standard/54989.html and http://www.itu.int/rec/T-REC-T.871.
A PDF file of the older JFIF 1.02 specification is available at
http://www.w3.org/Graphics/JPEG/jfif3.pdf.

The TIFF 6.0 file format specification can be obtained from
http://mirrors.ctan.org/graphics/tiff/TIFF6.ps.gz.  The JPEG incorporation
scheme found in the TIFF 6.0 spec of 3-June-92 has a number of serious
problems.  IJG does not recommend use of the TIFF 6.0 design (TIFF Compression
tag 6).  Instead, we recommend the JPEG design proposed by TIFF Technical Note
#2 (Compression tag 7).  Copies of this Note can be obtained from
http://www.ijg.org/files/.  It is expected that the next revision
of the TIFF spec will replace the 6.0 JPEG design with the Note's design.
Although IJG's own code does not support TIFF/JPEG, the free libtiff library
uses our library to implement TIFF/JPEG per the Note.


ARCHIVE LOCATIONS
=================

The "official" archive site for this software is www.ijg.org.
The most recent released version can always be found there in
directory "files".

The JPEG FAQ (Frequently Asked Questions) article is a source of some
general information about JPEG.  It is available at
http://www.faqs.org/faqs/jpeg-faq.


FILE FORMAT COMPATIBILITY
=========================

This software implements ITU T.81 | ISO/IEC 10918 with some extensions from
ITU T.871 | ISO/IEC 10918-5 (JPEG File Interchange Format-- see REFERENCES).
Informally, the term "JPEG image" or "JPEG file" most often refers to JFIF or
a subset thereof, but there are other formats containing the name "JPEG" that
are incompatible with the original JPEG standard or with JFIF (for instance,
JPEG 2000 and JPEG XR).  This software therefore does not support these
formats.  Indeed, one of the original reasons for developing this free software
was to help force convergence on a common, interoperable format standard for
JPEG files.

JFIF is a minimal or "low end" representation.  TIFF/JPEG (TIFF revision 6.0 as
modified by TIFF Technical Note #2) can be used for "high end" applications
that need to record a lot of additional data about an image.


TO DO
=====

Please send bug reports, offers of help, etc. to jpeg-info@jpegclub.org.

```

### freetype — LICENSE.TXT

```text
FREETYPE LICENSES
-----------------

The FreeType  2 font  engine is  copyrighted work  and cannot  be used
legally without  a software  license.  In order  to make  this project
usable to  a vast majority of  developers, we distribute it  under two
mutually exclusive open-source licenses.

This means that *you* must choose  *one* of the two licenses described
below, then obey all its terms and conditions when using FreeType 2 in
any of your projects or products.

  - The FreeType License,  found in the file  `docs/FTL.TXT`, which is
    similar to the  original BSD license *with*  an advertising clause
    that forces  you to explicitly  cite the FreeType project  in your
    product's  documentation.  All  details are  in the  license file.
    This license is suited to products which don't use the GNU General
    Public License.

    Note that  this license  is compatible to  the GNU  General Public
    License version 3, but not version 2.

  - The   GNU   General   Public   License   version   2,   found   in
    `docs/GPLv2.TXT`  (any  later  version  can  be  used  also),  for
    programs  which  already  use  the  GPL.  Note  that  the  FTL  is
    incompatible with GPLv2 due to its advertisement clause.

The contributed  BDF and PCF  drivers come  with a license  similar to
that  of the  X Window  System.   It is  compatible to  the above  two
licenses (see files `src/bdf/README`  and `src/pcf/README`).  The same
holds   for   the   source    code   files   `src/base/fthash.c`   and
`include/freetype/internal/fthash.h`; they were part of the BDF driver
in earlier FreeType versions.

The gzip  module uses the  zlib license (see  `src/gzip/zlib.h`) which
too is compatible to the above two licenses.

The   files   `src/autofit/ft-hb-ft.c`,   `src/autofit/ft-hb-decls.h`,
`src/autofit/ft-hb-types.h`,     and    `src/autofit/hb-script-list.h`
contain code taken (almost) verbatim  from the HarfBuzz library, which
uses the 'Old MIT' license compatible to the above two licenses.

The  MD5 checksum  support  (only used  for  debugging in  development
builds) is in the public domain.


--- end of LICENSE.TXT ---

```

### freetype — docs/FTL.TXT

```text
                    The FreeType Project LICENSE
                    ----------------------------

                            2006-Jan-27

                    Copyright 1996-2002, 2006 by
          David Turner, Robert Wilhelm, and Werner Lemberg



Introduction
============

  The FreeType  Project is distributed in  several archive packages;
  some of them may contain, in addition to the FreeType font engine,
  various tools and  contributions which rely on, or  relate to, the
  FreeType Project.

  This  license applies  to all  files found  in such  packages, and
  which do not  fall under their own explicit  license.  The license
  affects  thus  the  FreeType   font  engine,  the  test  programs,
  documentation and makefiles, at the very least.

  This  license   was  inspired  by  the  BSD,   Artistic,  and  IJG
  (Independent JPEG  Group) licenses, which  all encourage inclusion
  and  use of  free  software in  commercial  and freeware  products
  alike.  As a consequence, its main points are that:

    o We don't promise that this software works. However, we will be
      interested in any kind of bug reports. (`as is' distribution)

    o You can  use this software for whatever you  want, in parts or
      full form, without having to pay us. (`royalty-free' usage)

    o You may not pretend that  you wrote this software.  If you use
      it, or  only parts of it,  in a program,  you must acknowledge
      somewhere  in  your  documentation  that  you  have  used  the
      FreeType code. (`credits')

  We  specifically  permit  and  encourage  the  inclusion  of  this
  software, with  or without modifications,  in commercial products.
  We  disclaim  all warranties  covering  The  FreeType Project  and
  assume no liability related to The FreeType Project.


  Finally,  many  people  asked  us  for  a  preferred  form  for  a
  credit/disclaimer to use in compliance with this license.  We thus
  encourage you to use the following text:

   """
    Portions of this software are copyright © <year> The FreeType
    Project (https://freetype.org).  All rights reserved.
   """

  Please replace <year> with the value from the FreeType version you
  actually use.


Legal Terms
===========

0. Definitions
--------------

  Throughout this license,  the terms `package', `FreeType Project',
  and  `FreeType  archive' refer  to  the  set  of files  originally
  distributed  by the  authors  (David Turner,  Robert Wilhelm,  and
  Werner Lemberg) as the `FreeType Project', be they named as alpha,
  beta or final release.

  `You' refers to  the licensee, or person using  the project, where
  `using' is a generic term including compiling the project's source
  code as  well as linking it  to form a  `program' or `executable'.
  This  program is  referred to  as  `a program  using the  FreeType
  engine'.

  This  license applies  to all  files distributed  in  the original
  FreeType  Project,   including  all  source   code,  binaries  and
  documentation,  unless  otherwise  stated   in  the  file  in  its
  original, unmodified form as  distributed in the original archive.
  If you are  unsure whether or not a particular  file is covered by
  this license, you must contact us to verify this.

  The FreeType  Project is copyright (C) 1996-2000  by David Turner,
  Robert Wilhelm, and Werner Lemberg.  All rights reserved except as
  specified below.

1. No Warranty
--------------

  THE FREETYPE PROJECT  IS PROVIDED `AS IS' WITHOUT  WARRANTY OF ANY
  KIND, EITHER  EXPRESS OR IMPLIED,  INCLUDING, BUT NOT  LIMITED TO,
  WARRANTIES  OF  MERCHANTABILITY   AND  FITNESS  FOR  A  PARTICULAR
  PURPOSE.  IN NO EVENT WILL ANY OF THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE  FOR ANY DAMAGES CAUSED  BY THE USE OR  THE INABILITY TO
  USE, OF THE FREETYPE PROJECT.

2. Redistribution
-----------------

  This  license  grants  a  worldwide, royalty-free,  perpetual  and
  irrevocable right  and license to use,  execute, perform, compile,
  display,  copy,   create  derivative  works   of,  distribute  and
  sublicense the  FreeType Project (in  both source and  object code
  forms)  and  derivative works  thereof  for  any  purpose; and  to
  authorize others  to exercise  some or all  of the  rights granted
  herein, subject to the following conditions:

    o Redistribution of  source code  must retain this  license file
      (`FTL.TXT') unaltered; any  additions, deletions or changes to
      the original  files must be clearly  indicated in accompanying
      documentation.   The  copyright   notices  of  the  unaltered,
      original  files must  be  preserved in  all  copies of  source
      files.

    o Redistribution in binary form must provide a  disclaimer  that
      states  that  the software is based in part of the work of the
      FreeType Team,  in  the  distribution  documentation.  We also
      encourage you to put an URL to the FreeType web page  in  your
      documentation, though this isn't mandatory.

  These conditions  apply to any  software derived from or  based on
  the FreeType Project,  not just the unmodified files.   If you use
  our work, you  must acknowledge us.  However, no  fee need be paid
  to us.

3. Advertising
--------------

  Neither the  FreeType authors and  contributors nor you  shall use
  the name of the  other for commercial, advertising, or promotional
  purposes without specific prior written permission.

  We suggest,  but do not require, that  you use one or  more of the
  following phrases to refer  to this software in your documentation
  or advertising  materials: `FreeType Project',  `FreeType Engine',
  `FreeType library', or `FreeType Distribution'.

  As  you have  not signed  this license,  you are  not  required to
  accept  it.   However,  as  the FreeType  Project  is  copyrighted
  material, only  this license, or  another one contracted  with the
  authors, grants you  the right to use, distribute,  and modify it.
  Therefore,  by  using,  distributing,  or modifying  the  FreeType
  Project, you indicate that you understand and accept all the terms
  of this license.

4. Contacts
-----------

  There are two mailing lists related to FreeType:

    o freetype@nongnu.org

      Discusses general use and applications of FreeType, as well as
      future and  wanted additions to the  library and distribution.
      If  you are looking  for support,  start in  this list  if you
      haven't found anything to help you in the documentation.

    o freetype-devel@nongnu.org

      Discusses bugs,  as well  as engine internals,  design issues,
      specific licenses, porting, etc.

  Our home page can be found at

    https://freetype.org


--- end of FTL.TXT ---

```

### freetype — src/bdf/README

```text
                  FreeType font driver for BDF fonts

                       Francesco Zappa Nardelli
                  <francesco.zappa.nardelli@ens.fr>


Introduction
************

BDF (Bitmap Distribution Format) is a bitmap font format defined by Adobe,
which is intended to be easily understood by both humans and computers.
This code implements a BDF driver for the FreeType library, following the
Adobe Specification V 2.2.  The specification of the BDF font format is
available from Adobe's web site:

  https://adobe-type-tools.github.io/font-tech-notes/pdfs/5005.BDF_Spec.pdf

Many good bitmap fonts in bdf format come with XFree86 (www.XFree86.org).
They do not define vertical metrics, because the X Consortium BDF
specification has removed them.


Encodings
*********

[This section is out of date, retained for historical reasons.  BDF
 properties can be retrieved with `FT_Get_BDF_Property`, character set ID
 values with `FT_Get_BDF_Charset_ID`.]

The variety of encodings that accompanies bdf fonts appears to encompass the
small set defined in freetype.h.  On the other hand, two properties that
specify encoding and registry are usually defined in bdf fonts.

I decided to make these two properties directly accessible, leaving to the
client application the work of interpreting them.  For instance:


  #include FT_INTERNAL_BDF_TYPES_H

  FT_Face          face;
  BDF_Public_Face  bdfface;


  FT_New_Face( library, ..., &face );

  bdfface = (BDF_Public_Face)face;

  if ( ( bdfface->charset_registry == "ISO10646" ) &&
       ( bdfface->charset_encoding == "1" )        )
    [..]


Thus the driver always exports `ft_encoding_none' as face->charmap.encoding.
FT_Get_Char_Index's behavior is unmodified, that is, it converts the ULong
value given as argument into the corresponding glyph number.

If the two properties are not available, Adobe Standard Encoding should be
assumed.


Anti-Aliased Bitmaps
********************

The driver supports an extension to the BDF format as used in Mark Leisher's
xmbdfed bitmap font editor.  Microsoft's SBIT tool expects bitmap fonts in
that format for adding anti-aliased them to TrueType fonts.  It introduces a
fourth field to the `SIZE' keyword which gives the bpp value (bits per
pixel) of the glyph data in the font.  Possible values are 1 (the default),
2 (four gray levels), 4 (16 gray levels), and 8 (256 gray levels).  The
driver returns either a bitmap with 1 bit per pixel or a pixmap with 8bits
per pixel (using 4, 16, and 256 gray levels, respectively).


Known problems
**************

- A font is entirely loaded into memory.  Obviously, this is not the Right
  Thing(TM).  If you have big fonts I suggest you convert them into PCF
  format (using the bdftopcf utility): the PCF font drive of FreeType can
  perform incremental glyph loading.

When I have some time, I will implement on-demand glyph parsing.

- Except for encodings properties, client applications have no visibility of
  the PCF_Face object.  This means that applications cannot directly access
  font tables and must trust FreeType.

- Currently, glyph names are ignored.

  I plan to give full visibility of the BDF_Face object in an upcoming
  revision of the driver, thus implementing also glyph names.

- As I have never seen a BDF font that defines vertical metrics, vertical
  metrics are (parsed and) discarded.  If you own a BDF font that defines
  vertical metrics, please let me know (I will implement them in 5-10
  minutes).


License
*******

Copyright (C) 2001-2002 by Francesco Zappa Nardelli

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*** Portions of the driver (that is, bdflib.c and bdf.h):

Copyright 2000 Computing Research Labs, New Mexico State University
Copyright 2001-2002, 2011 Francesco Zappa Nardelli

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
THE COMPUTING RESEARCH LAB OR NEW MEXICO STATE UNIVERSITY BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Credits
*******

This driver is based on excellent Mark Leisher's bdf library.  If you
find something good in this driver you should probably thank him, not
me.

```

### freetype — src/pcf/README

```text
                  FreeType font driver for PCF fonts

                       Francesco Zappa Nardelli
                  <francesco.zappa.nardelli@ens.fr>


Introduction
************

PCF (Portable Compiled Format) is a binary bitmap font format, largely used
in X world. This code implements a PCF driver for the FreeType library.
Glyph images are loaded into memory only on demand, thus leading to a small
memory footprint.

Information on the PCF font format can only be worked out from
`pcfread.c', and `pcfwrite.c', to be found, for instance, in the XFree86
(www.xfree86.org) source tree (xc/lib/font/bitmap/).

Many good bitmap fonts in bdf format come with XFree86: they can be
compiled into the pcf format using the `bdftopcf' utility.


Supported hardware
******************

The driver has been tested on linux/x86 and sunos5.5/sparc.  In both
cases the compiler was gcc.  When back in Paris, I will test it also
on linux/alpha.


Encodings
*********

Use `FT_Get_BDF_Charset_ID' to access the encoding and registry.

The driver always exports `ft_encoding_none' as face->charmap.encoding.
FT_Get_Char_Index() behavior is unmodified, that is, it converts the ULong
value given as argument into the corresponding glyph number.


Known problems
**************

- dealing explicitly with encodings breaks the uniformity of FreeType 2
  API.

- except for encodings properties, client applications have no
  visibility of the PCF_Face object.  This means that applications
  cannot directly access font tables and are obliged to trust
  FreeType.

- currently, glyph names and ink_metrics are ignored.

I plan to give full visibility of the PCF_Face object in the next
release of the driver, thus implementing also glyph names and
ink_metrics.

- height is defined as (ascent - descent).  Is this correct?

- if unable to read size information from the font, PCF_Init_Face
  sets available_size->width and available_size->height to 12.

- too many english grammar errors in the readme file :-(


License
*******

Copyright (C) 2000 by Francesco Zappa Nardelli

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Credits
*******

Keith Packard wrote the pcf driver found in XFree86.  His work is at
the same time the specification and the sample implementation of the
PCF format.  Undoubtedly, this driver is inspired from his work.

```

### Pillow 13.0.0 — LICENSE

```text
The Python Imaging Library (PIL) is

    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh and contributors

Pillow is the friendly PIL fork. It is

    Copyright © 2010 by Jeffrey 'Alex' Clark and contributors

Like PIL, Pillow is licensed under the open source MIT-CMU License:

By obtaining, using, and/or copying this software and/or its associated
documentation, you agree that you have read, understood, and will comply
with the following terms and conditions:

Permission to use, copy, modify and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appears in all copies, and that
both that copyright notice and this permission notice appear in supporting
documentation, and that the name of Secret Labs AB or the author not be
used in advertising or publicity pertaining to distribution of the software
without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL,
INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

```
