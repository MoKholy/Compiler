#pragma once
#include <string>
#include <exception>
#include <vector>
#include <optional>
#include <memory>
// Create Custom Exception 
class SyntaxError : public std::exception {
private:
    std::string line = "Line: ";
    std::string out = "Expected: ";
    std::string out2 = " But got: ";
    std::string out_final;

public:
    SyntaxError(const std::vector<std::string>& expected_tokens, const std::string& token, const std::string &line_num) {
        for (const auto& tok : expected_tokens) {
            out += tok + ", ";
        }
        out.back() = ' '; // Replace the last comma
        out2 += token;
        out_final = line + line_num + " " + out + out2;
    }

    const char* what() const noexcept override {
        return out_final.c_str();
    }
};



struct Token {
    std::string type;
    std::string val;
    std::string line_num;
    Token() = default;
    Token(const std::string& type, const std::string& val, const std::string line_num) : type(type), val(val), line_num(line_num) {}
};



// Parser class


class parser {
private:
    size_t curr_token_idx = 0;
    std::optional<Token> curr_token;
    int current_line = 0;
    std::string input_file_path;
    std::string output_filepath;
    std::unique_ptr<std::vector<Token>> tokens_vector;
    std::optional<Token> get_next_token();
    std::unique_ptr<std::vector<Token>> get_tokens();
public:
    parser(const std::string& input_file_path_, const std::string& output_filepath_);
    void run();
    void parse();
    // Function to match a vector of expected tokens
    bool match(const std::vector<std::string>& expectedTokens, const std::string& token, const std::string &line_num);

    // Overloaded function to match a single expected token
    bool match(const std::string& expectedToken, const std::string& token, const std::string& line_num);
    // function to unput a token
    bool unput_token();

    // GRAMMAR RULES
    bool program();
    bool declaration_list();
    bool declaration_list_prime();
    bool declaration();
    bool var_declaration();
    bool var_declaration_prime();
    bool type_specifier();
    bool params();
    bool param_list();
    bool param_list_prime();
    bool param();
    bool param_prime();
    bool compound_stmt();
    bool statement_list();
    bool statement();
    bool selection_stmt();
    bool selection_stmt_prime();
    bool iteration_stmt();
    bool assignment_stmt();
    bool expression();
    bool expression_prime();
    bool var();
    bool var_prime();
    bool relop();
    bool additive_expression();
    bool additive_expression_prime();
    bool addop();
    bool term();
    bool term_prime();
    bool mulop();
    bool factor();

};