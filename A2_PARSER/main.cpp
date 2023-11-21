#include <iostream>
#include "parser.h"
using namespace std;


int main() {
    parser RDP  = parser("sample3_error_lex.txt", "parse_file.txt");
    RDP.run();
    cout << "Parsing Complete MAIN" << endl;
    return 0;
}