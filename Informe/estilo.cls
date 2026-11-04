\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{estilo}
\LoadClass[10pt]{article}

\RequirePackage[table]{xcolor}   % antes de tikz, para poder colorear tablas
\RequirePackage{hyperref}
\RequirePackage{verbatim}
\RequirePackage{attachfile2}
\RequirePackage{etoolbox}
\RequirePackage{xparse}
\RequirePackage{pgffor}
\RequirePackage{arrayjobx}
\RequirePackage{graphicx}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage[document]{ragged2e}
\RequirePackage{lipsum}
\RequirePackage{translations}
\RequirePackage{ifthen}
\RequirePackage{xstring}
\RequirePackage[a4paper, left=30mm, right=30mm, top=30mm, bottom=30mm, marginpar=25mm]{geometry}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}   % versalitas en negrita/cursiva y acentos correctos
\RequirePackage{lmodern}       % misma letra Computer Modern, versión escalable
\RequirePackage{csquotes}

\RequirePackage{tikz}

\RequirePackage{xfp}

%------------------------------------------------------------------------------
%	Paquetes agregados para el informe
%------------------------------------------------------------------------------
\RequirePackage{amsmath}       % amsthm debe cargarse después de amsmath
\RequirePackage{amsthm}
\RequirePackage{booktabs}
\RequirePackage[font=small,labelfont={bf,color=ucazul}]{caption}
\RequirePackage{titlesec}
\RequirePackage[most]{tcolorbox}

%------------------------------------------------------------------------------
%	COLORES UNIVERSIDAD DE CALDAS
%	Ajuste estos tres valores si el manual de identidad indica otros códigos.
%------------------------------------------------------------------------------
\definecolor{ucazul}{RGB}{0,45,98}        % azul institucional (principal)
\definecolor{ucdorado}{RGB}{196,154,40}   % dorado (acento)
\definecolor{uccielo}{RGB}{232,238,247}   % azul muy claro (fondos)

% Nombres usados dentro de las figuras del informe
\colorlet{institucional}{ucazul}
\colorlet{institucionalclaro}{uccielo}

%------------------------------------------------------------------------------
%	Datos del informe (se definen en main.tex)
%------------------------------------------------------------------------------
\newcommand{\universidad}[1]{\gdef\@universidad{#1}}
\newcommand{\facultad}[1]{\gdef\@facultad{#1}}
\newcommand{\programa}[1]{\gdef\@programa{#1}}
\newcommand{\curso}[1]{\gdef\@curso{#1}}
\newcommand{\docente}[1]{\gdef\@docente{#1}}
\newcommand{\integrantes}[1]{\gdef\@integrantes{#1}}
\newcommand{\subtitulo}[1]{\gdef\@subtitulo{#1}}
\newcommand{\entrega}[1]{\gdef\@entrega{#1}}

\universidad{Universidad de Caldas}
\facultad{Facultad de Ingenierías}
\programa{Ingeniería de Sistemas y Computación}
\curso{Análisis y Diseño de Algoritmos}
\docente{Nombre del docente}
\integrantes{Integrante 1 & Código \\ Integrante 2 & Código}
\subtitulo{}
\entrega{Proyecto Semestral 2026-2}

% Logo: si no existe logo.pdf/png, se omite sin generar error
\newcommand{\logo}[1]{\IfFileExists{logo.pdf}{\includegraphics[width=#1]{logo}}%
  {\IfFileExists{logo.png}{\includegraphics[width=#1]{logo}}{}}}

%------------------------------------------------------------------------------
%	Función para poner los asteriscos (ahora en azul y dorado)
%------------------------------------------------------------------------------
\newcommand{\andreas}[5][1.0]{
    \begin{scope}[shift={(#2,#3)},rotate=45,scale=#4,transparency group,opacity=#1]
        \fill[fill=#5] (0,0) -- (0,1) -- (3,1) -- (3,0);
        \fill[fill=#5] (1,-1) -- (2,-1) -- (2,2) -- (1,2);
    \end{scope}
}

\newcommand{\andreasline}{
    \centering\begin{tikzpicture}
        \newcommand\numcross{29}
        \foreach \n in {1,...,\the\numexpr\numcross\relax} {
            \ifodd\n
              \andreas[\fpeval{0.9*sin((\n + 1)*pi/(\numcross+2))}]{0.5*\n}{0}{0.10}{ucazul}
            \else
              \andreas[\fpeval{0.9*sin((\n + 1)*pi/(\numcross+2))}]{0.5*\n}{0}{0.10}{ucdorado}
            \fi
        }
    \end{tikzpicture}
}

\newcommand{\andreaslineslim}{
    \centering\begin{tikzpicture}[baseline]
        \newcommand\numcross{74}
        \foreach \n in {1,...,\the\numexpr\numcross\relax} {
            \andreas[0.75]{0.2*\n}{0}{0.04}{ucazul}
        }
    \end{tikzpicture}
}

%------------------------------------------------------------------------------
%	Función para contar palabras
%------------------------------------------------------------------------------
\newcommand{\quickwordcount}[1]{%
  \immediate\write18{texcount -total -sum -1 -merge #1.tex > #1-words}%
  \input{#1-words} palabras%
}

%------------------------------------------------------------------------------
%	HEADERS, FOOTERS EN SECCIONES
%------------------------------------------------------------------------------
\pagestyle{fancy}
\setlength{\headheight}{27pt}

\renewcommand{\headrulewidth}{1pt}
\renewcommand{\footrulewidth}{1pt}
\renewcommand{\headrule}{{\color{ucazul}\hrule height \headrulewidth width \headwidth \vskip-\headrulewidth}}
\renewcommand{\footrule}{{\color{ucdorado}\vskip-\footruleskip\vskip-\footrulewidth
  \hrule height \footrulewidth width \headwidth \vskip\footruleskip}}
\rhead{\footnotesize\color{ucazul} \textsc {\@entrega\\ \@curso}}
\lhead{\logo{2.5cm}}
\cfoot{\small\color{ucazul} \textsc {Página \thepage\ de \pageref*{LastPage}}}

\fancypagestyle{firststyle}
 {
  \fancyhf{}
   \renewcommand{\headrulewidth}{0pt}
   \renewcommand{\footrulewidth}{0pt}
   % descomentar si les interesa poner la cantidad de palabras:
   %\lfoot{\textit {\quickwordcount{main}}}
 }

%------------------------------------------------------------------------------
%	TÍTULOS DE SECCIÓN
%------------------------------------------------------------------------------
\titleformat{\section}
  {\Large\bfseries\color{ucazul}}
  {\colorbox{ucazul}{\color{white}\thesection}}
  {0.6em}{}
  [{\color{ucdorado}\titlerule[1.2pt]}]
\titleformat{\subsection}
  {\large\bfseries\color{ucazul}}{\thesubsection}{0.6em}{}
\titleformat{\subsubsection}
  {\normalsize\bfseries\color{ucazul!80!black}}{\thesubsubsection}{0.6em}{}
\titleformat{\paragraph}[runin]
  {\normalsize\bfseries\color{ucazul}}{}{0pt}{}

%------------------------------------------------------------------------------
%	CARÁTULA
%------------------------------------------------------------------------------
\renewcommand*{\maketitle}{
\thispagestyle{firststyle}
\begin{tikzpicture}[remember picture,overlay]
  % franja superior azul con línea dorada
  \fill[ucazul] (current page.north west) rectangle ([yshift=-3.0cm]current page.north east);
  \fill[ucdorado] ([yshift=-3.0cm]current page.north west) rectangle ([yshift=-3.25cm]current page.north east);
  \node[text=white,font=\LARGE\bfseries\scshape] at ([yshift=-1.25cm]current page.north) {\@universidad};
  \node[text=white,font=\small\scshape] at ([yshift=-2.15cm]current page.north) {\@facultad\ --- \@programa};
  % franja inferior
  \fill[ucdorado] ([yshift=1.25cm]current page.south west) rectangle ([yshift=1.0cm]current page.south east);
  \fill[ucazul] (current page.south west) rectangle ([yshift=1.0cm]current page.south east);
\end{tikzpicture}
\begin{center}
\vspace*{1.2cm}
	% Se usa \par y \vspace en lugar de \\ para que no falle si no hay logo
	{\logo{6cm}\par}
	\vspace{1cm}
	{\color{ucazul}\Large\scshape \@curso\par}
	\vspace{0.6cm}
	{\color{ucdorado}\large\bfseries\scshape \@entrega\par}
	\vspace{0.3cm}
	{\color{ucazul}\huge\bfseries \@title\par}
	\vspace{0.4cm}
	\ifx\@subtitulo\@empty\else
	  {\large\itshape\color{ucazul!80!black} \@subtitulo\par}
	  \vspace{0.4cm}
	\fi
	{\andreasline\par}
	\vspace{0.3cm}
	{\large \@date\par}
	\vspace{1cm}
	\begin{tcolorbox}[enhanced, width=0.7\textwidth, colback=uccielo, colframe=ucazul,
	  boxrule=0.8pt, arc=2mm, halign=center, fonttitle=\bfseries\scshape,
	  title={Integrantes}, coltitle=white, colbacktitle=ucazul, center]
	  {\large\begin{tabular}{ll}
	    \@integrantes
	  \end{tabular}}
	\end{tcolorbox}
	\vspace{0.6cm}
	{\large {\color{ucazul}\textsc{Docente:}} \@docente}
 \end{center}
}

%------------------------------------------------------------------------------
%	TEOREMAS, DEFINICIONES Y CAJAS DE COLOR
%------------------------------------------------------------------------------
\theoremstyle{definition}
\newtheorem{definicion}{Definición}[section]
\newtheorem{ejemplo}[definicion]{Ejemplo}
\theoremstyle{plain}
\newtheorem{teorema}[definicion]{Teorema}
\newtheorem{lema}[definicion]{Lema}
\newtheorem{corolario}[definicion]{Corolario}
\theoremstyle{remark}
\newtheorem{observacion}[definicion]{Observación}

\tcbset{ucbase/.style={enhanced, breakable, sharp corners, boxrule=0pt,
  left=6pt, right=6pt, top=4pt, bottom=4pt, before skip=8pt, after skip=8pt}}
\tcolorboxenvironment{definicion}{ucbase, colback=uccielo, borderline west={3pt}{0pt}{ucazul}}
\tcolorboxenvironment{teorema}{ucbase, colback=ucdorado!10, borderline west={3pt}{0pt}{ucdorado}}
\tcolorboxenvironment{lema}{ucbase, colback=ucdorado!10, borderline west={3pt}{0pt}{ucdorado}}
\tcolorboxenvironment{corolario}{ucbase, colback=ucdorado!10, borderline west={3pt}{0pt}{ucdorado}}
\tcolorboxenvironment{observacion}{ucbase, colback=gray!6, borderline west={3pt}{0pt}{gray!60}}
\tcolorboxenvironment{ejemplo}{ucbase, colback=gray!6, borderline west={3pt}{0pt}{ucazul!60}}

% Nombre de los teoremas en azul
\patchcmd{\@begintheorem}{\thm@headfont}{\thm@headfont\color{ucazul}}{}{}
% Cuadrito de fin de demostración en dorado
\renewcommand{\qedsymbol}{\textcolor{ucdorado}{$\blacksquare$}}

% Caja para resultados finales (cotas O, Θ, Ω)
\newcommand{\resultado}[1]{%
  \begin{tcolorbox}[enhanced, colback=uccielo, colframe=ucazul, boxrule=1pt, arc=2mm,
    halign=center, width=0.92\linewidth, center, before skip=8pt, after skip=8pt]
  #1
  \end{tcolorbox}}

%------------------------------------------------------------------------------
%	TABLAS Y ENLACES
%------------------------------------------------------------------------------
\hypersetup{colorlinks=true, linkcolor=ucazul, citecolor=ucdorado!80!black, urlcolor=ucazul}
\AtBeginDocument{\arrayrulecolor{ucazul}}

\endinput
