#include "parser.h"
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
using namespace std;

parser::parser(const std::string&input_file_path_, const std::string&output_filepath_) {
	input_file_path = input_file_path_;
	output_filepath = output_filepath_;
	curr_token_idx = 0;
	// get tokens
	tokens_vector = get_tokens();
	curr_token = get_next_token();
}
std::unique_ptr<std::vector<Token>> parser::get_tokens() {

	std::unique_ptr<std::vector<Token>> tokens_vector_ = std::make_unique<std::vector<Token>>();

	//cout << input_file_path << endl;
	// read from file
	ifstream input;
	input.open((input_file_path).c_str());
	if (!input.is_open()) {
		cout << "Error: could not open file" << endl;
		return nullptr;
	}
	else {
		string line;
		while (getline(input, line)) {
			std::istringstream iss(line);
			string type;
			string val;
			int line_num;
			if (!(iss >> val >> line_num)) {
				cout << "Error: could not read line" << endl;
				return nullptr;
			}
			else {
				cout << val << " " << line_num << endl;
				//cout << val << endl;
				Token token;
				//token.type = type;
				token.val = val;
				token.line_num = to_string(line_num);
				tokens_vector_->push_back(token);
			}
		}
		input.close();
	}

	return tokens_vector_;
}

std::optional<Token> parser::get_next_token() {
	if (curr_token_idx < tokens_vector->size()) {
		return (*tokens_vector)[curr_token_idx++];
	}
	else {
		return std::nullopt;
	}
}

void parser::run() {

	// read tokens first 
	cout << "Parsing..." << endl;
	parse();
	cout << "Parsing Successful" << endl;
}

void parser::parse() {
	cout << "parse" << endl;
	program();
}

bool parser::match(const std::vector<std::string>& expectedTokens, const std::string& token, const std::string &line_num) {
	try {
		// check if token in expectedToken vector
		for (auto exp_tok : expectedTokens) {
			if (exp_tok == token) {
				cout << "matched " << token << " expected: " << exp_tok << endl;
				// advance token
				curr_token = get_next_token();
				return true;
			}
		}
		throw SyntaxError(expectedTokens, token, line_num);
	}
	catch (SyntaxError& ex) {
		std::cerr << ex.what() << endl;
		exit(0);
	}
	return true;
}

bool parser::match(const std::string& expectedToken, const std::string& token, const std::string& line_num) {
	std::vector<std::string> expectedTokens = { expectedToken };
	return match(expectedTokens, token, line_num);
}

bool parser::unput_token() {
	if (curr_token_idx > 0) {
		curr_token_idx--;
		curr_token = (*tokens_vector)[curr_token_idx];
		return true;
	}
	else {
		return false;
	}
}

bool parser::program() {
	cout << "program" << endl;
	// program -> Program ID { declaration-list statement-list}
	cout << "curr_token: " << curr_token.value().val << endl;
	if (curr_token.has_value()) {
		match("Program", curr_token.value().val, curr_token.value().line_num);
	}

	if (curr_token.has_value()) {
		match("ID", curr_token.value().val, curr_token.value().line_num);
	}

	if (curr_token.has_value()) {
		match("{", curr_token.value().val, curr_token.value().line_num);
	}
	declaration_list();
	cout << "matched declaration_list" << endl;
	statement_list();

	if (curr_token.has_value()) {
		match("}", curr_token.value().val, curr_token.value().line_num);
	}
	cout << "matched }" << endl;
	return true;
}

bool parser::declaration_list() {
	cout << "declaration_list" << endl;
	declaration();
	declaration_list_prime();
	return true;
}

bool parser::declaration_list_prime() {
	cout << "declaration_list_prime" << endl;
	declaration();
	while (curr_token.has_value() && (curr_token.value().val == "int" || curr_token.value().val == "float")) {
		declaration();
	}
	//unput_token(); //epsilon
	return true;
}

bool parser::declaration() {
	cout << "declaration" << endl;
	var_declaration();
	return true;
}

bool parser::var_declaration() {
	cout << "var_declaration" << endl;
	type_specifier();
	if (curr_token.has_value()) {
		match("ID", curr_token.value().val, curr_token.value().line_num);
	}
	var_declaration_prime();
	return true;
}

bool parser::var_declaration_prime() {
	cout << "var_declaration_prime" << endl;
	if (curr_token.has_value()) {
		if (curr_token.value().val == ";") {
			match(";", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "[") {
			match("[", curr_token.value().val, curr_token.value().line_num);
			curr_token = get_next_token();
			if (curr_token.has_value()) {
				match("NUM", curr_token.value().val, curr_token.value().line_num);
			}
			curr_token = get_next_token();
			if (curr_token.has_value()) {
				match("]", curr_token.value().val, curr_token.value().line_num);
			}
			curr_token = get_next_token();
			if (curr_token.has_value()) {
				match(";", curr_token.value().val, curr_token.value().line_num);
			}
		}
	}
	/*else {
		cout << "unput_token" << endl;
		unput_token();
	}*/
	return true;
}

bool parser::type_specifier() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "int") {
			match("int", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "float") {
			match("float", curr_token.value().val, curr_token.value().line_num);
		}
	}
	return true;
}

bool parser::params() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "void") {
			match("void", curr_token.value().val, curr_token.value().line_num);
			return true;
		}
		else {
			param_list();
			return true;
		}
	}
	return true;
}

bool parser::param_list() {
	param();
	param_list_prime();
	return true;
}

bool parser::param_list_prime() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == ",") {
			match(",", curr_token.value().val, curr_token.value().line_num);
			param();
			param_list_prime();
		}
	}
	return true;
}

bool parser::param() {
	type_specifier();
	match("ID", curr_token.value().val, curr_token.value().line_num);
	param_prime();
	return true;
}
bool parser::param_prime() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "[") {
			match("[", curr_token.value().val, curr_token.value().line_num);
			match("]", curr_token.value().val, curr_token.value().line_num);
		}
	}
	/*else {
		unput_token();
	}*/
	return true;
}

bool parser::compound_stmt() {
	cout << "compound_stmt" << endl;
	if (curr_token.has_value()) {
		match("{", curr_token.value().val, curr_token.value().line_num);
		statement_list();
		match("}", curr_token.value().val, curr_token.value().line_num);
	}
	return true;
}

bool parser::statement_list() {
	while (curr_token.has_value() && (curr_token.value().val == "if" || curr_token.value().val == "while" || curr_token.value().val == "return" || curr_token.value().val == "ID" || curr_token.value().val == "{")) {
		statement();
	}
	return true;
}

bool parser::statement() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "if") {
			selection_stmt();
		}
		else if (curr_token.value().val == "while") {
			iteration_stmt();
		}
		else if (curr_token.value().val == "ID") {
			assignment_stmt();
		}
		else if (curr_token.value().val == "{") {
			compound_stmt();
		}
		else {
			throw SyntaxError({ "if", "while", "ID", "{" }, curr_token.value().val, curr_token.value().line_num);
		}
	}
	return true;
}

bool parser::selection_stmt() {
	if (curr_token.has_value()) {
		match("if", curr_token.value().val, curr_token.value().line_num);
		match("(", curr_token.value().val, curr_token.value().line_num);
		expression();
		match(")", curr_token.value().val, curr_token.value().line_num);
		statement();
		selection_stmt_prime();
	}
	else {
		throw SyntaxError({ "if" }, "Nothing", curr_token.value().line_num);
	}
}

bool parser::selection_stmt_prime() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "else") {
			match("else", curr_token.value().val, curr_token.value().line_num);
			statement();
		}
	}
	return true;
}

bool parser::iteration_stmt() {
	if (curr_token.has_value()) {
		match("while", curr_token.value().val, curr_token.value().line_num);
		match("(", curr_token.value().val, curr_token.value().line_num);
		expression();
		match(")", curr_token.value().val, curr_token.value().line_num);
		statement();
	}
	else {
		throw SyntaxError({ "while" }, "Nothing", curr_token.value().line_num);
	}
}

bool parser::assignment_stmt() {
	if (curr_token.has_value()) {
		var();
		match("=", curr_token.value().val, curr_token.value().line_num);
		expression();
		match(";", curr_token.value().val, curr_token.value().line_num);
	}
	else {
		throw SyntaxError({ "ID" }, "Nothing", curr_token.value().line_num);
	}
}
bool parser::var() {
	if (curr_token.has_value()) {
		match("ID", curr_token.value().val, curr_token.value().line_num);
		var_prime();
	}
	else {
		throw SyntaxError({ "ID" }, "Nothing", curr_token.value().line_num);
	}
}
bool parser::var_prime() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "[") {
			match("[", curr_token.value().val, curr_token.value().line_num);
			expression();
			match("]", curr_token.value().val, curr_token.value().line_num);
		}
	}
	return true;
}

bool parser::expression() {
	cout << "expression" << endl;
	additive_expression();
	expression_prime();
	return true;
}

bool parser::expression_prime() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "<=" || curr_token.value().val == "<" || curr_token.value().val == ">" || curr_token.value().val == ">=" || curr_token.value().val == "==" || curr_token.value().val == "!=") {
			relop();
			additive_expression();
		}
	}
	return true;
}

bool parser::relop() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "<=") {
			match("<=", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "<") {
			match("<", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == ">") {
			match(">", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == ">=") {
			match(">=", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "==") {
			match("==", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "!=") {
			match("!=", curr_token.value().val, curr_token.value().line_num);
		}
		else {
			throw SyntaxError({ "<=", "<", ">", ">=", "==", "!=" }, curr_token.value().val, curr_token.value().line_num);
		}
	}
	return true;
}

bool parser::additive_expression() {
	cout << "additive_expression" << endl;
	term();
	additive_expression_prime();
	return true;
}

bool parser::additive_expression_prime() {
	cout << "additive_expression_prime" << endl;
	cout << "curr_token: " << curr_token.value().val << endl;
	if (curr_token.has_value()) {
		if (curr_token.value().val == "+" || curr_token.value().val == "-") {
			addop();
			term();
			additive_expression_prime();
		}
	}
	return true;
}

bool parser::addop() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "+") {
			match("+", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "-") {
			match("-", curr_token.value().val, curr_token.value().line_num);
		}
		else {
			throw SyntaxError({ "+", "-" }, curr_token.value().val, curr_token.value().line_num);
		}
	}
}

bool parser::term() {
	cout << "term" << endl;
	factor();
	term_prime();
	return true;
}

bool parser::term_prime() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "*" || curr_token.value().val == "/") {
			mulop();
			factor();
			term_prime();
		}
	}
	return true;
}

bool parser::mulop() {
	if (curr_token.has_value()) {
		if (curr_token.value().val == "*") {
			match("*", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "/") {
			match("/", curr_token.value().val, curr_token.value().line_num);
		}
		else {
			throw SyntaxError({ "*", "/" }, curr_token.value().val, curr_token.value().line_num);
		}
	}
}

bool parser::factor() {
	cout << "factor" << endl;
	if (curr_token.has_value()) {
		if (curr_token.value().val == "(") {
			match("(", curr_token.value().val, curr_token.value().line_num);
			expression();
			match(")", curr_token.value().val, curr_token.value().line_num);
		}
		else if (curr_token.value().val == "ID") {
			var();
		}
		else if (curr_token.value().val == "NUM") {
			match("NUM", curr_token.value().val, curr_token.value().line_num);
		}
		else {
			throw SyntaxError({ "(", "ID", "NUM" }, curr_token.value().val, curr_token.value().line_num);
		}
	}
}
