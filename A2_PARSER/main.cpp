#include <iostream>
#include "parser.h"
using namespace std;


int main() {

    /*cout << "Throw error" << endl;
    try {
        vector<string> x = { "ID", "NUM" };

        throw SyntaxError(x, "LOL");
    }
    catch (SyntaxError& ex) {
        std::cout << ex.what() << std::endl;
    }

    return 0;*/

    cout << "Starting Parsing" << endl;

    parser RDP;
    RDP.input_file_path = "lex_file.txt";
    RDP.output_filepath = "parse_file.txt";
    RDP.tokens_vector = RDP.get_tokens();
    RDP.run();
    cout << "Parsing Complete MAIN" << endl;
    return 0;
}