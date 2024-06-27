with (import <nixpkgs> {});
mkShell {
  buildInputs = with python312Packages; [
    openpyxl
    requests
    tkinter
    beautifulsoup4
    certifi
  ];
}
