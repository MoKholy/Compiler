#include "parser.h"
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
using namespace std;


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
			//cout << line << endl;
			// split line into token components
			std::istringstream iss(line);
			string type;
			string val;
			string line_num;

			/*if (!(iss >> type >> val >> line_num)) {
				cout << "Error: could not read line" << endl;
				return nullptr;
			}*/
			if (!(iss >> val)) {
				cout << "Error: could not read line" << endl;
				return nullptr;
			}
			else {
				//cout << type << " " << val << " " << line_num << endl;
				//cout << val << endl;
				Token token;
				//token.type = type;
				token.val = val;
				//token.line_num = stoi(line_num);
				tokens_vector_->push_back(token);
			}
		}
		input.close();

		// print tokens
		//for (auto token : *tokens_vector) {
		//	//cout << token.val << " " << token.type << " " << token.line_num << endl;
		//	cout << token.val << endl;
		//}
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
	//ofstream ofs;
	//ofs.open(output_filepath.c_str(), ofstream::app);

	//// check if file is open
	//if (!ofs.is_open()) {
	//	cout << "Error: could not open file" << endl;
	//	return;
	//}
	//else {
	//	parse();
	//}
	//ofs.close();
	cout << "Parsing..." << endl;
	parse();
	cout << "Parsing Successful" << endl;
}

void parser::parse() {
	cout << "parse" << endl;
	program();
}

bool parser::match(const std::vector<std::string>& expectedTokens, const std::string& token) {
	try {
		// check if token in expectedToken vector
		for (auto exp_tok : expectedTokens) {
			if (exp_tok == token) {
				cout << "matched " << token << " expected: " << exp_tok << endl;
				return true;
			}
		}

		throw SyntaxError(expectedTokens, token);
	}
	catch (SyntaxError& ex) {
		std::cout << ex.what() << endl;
	}
	return true;

	//ofstream out;
	//out.open(output_filepath.c_str(), ios::app);

	//if (out.is_open()) {

	//	try {
	//		// check if token in expectedToken vector
	//		for (auto exp_tok : expectedTokens) {
	//			if (exp_tok == token) {
	//				return true;
	//			}
	//		}

	//		throw SyntaxError(expectedTokens, token);
	//	}
	//	catch (SyntaxError& ex) {
	//		std::cout << ex.what() << endl;
	//	}
	//}
	//else {
	//	std::cout << "File not opened" << std::endl;
	//}
}
bool parser::match(const std::string& expectedToken, const std::string& token) {
	std::vector<std::string> expectedTokens = { expectedToken };
	return match(expectedTokens, token);
}
bool parser::unput_token() {
	if (curr_token_idx > 0) {
		curr_token_idx--;
		return true;
	}
	else {
		return false;
	}
}

bool parser::program() {
	cout << "program" << endl;
	// program -> Program ID { declaration-list statement-list}
	auto curr_token = get_next_token();

	cout << "curr_token: " << curr_token.value().val << endl;
	if (curr_token.has_value()) {
		match("Program", curr_token.value().val);
	}

	curr_token = get_next_token();

	if (curr_token.has_value()) {
		match("ID", curr_token.value().val);
	}
	curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("{", curr_token.value().val);
	}
	declaration_list();
	cout << "matched declaration_list" << endl;
	statement_list();

	curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("}", curr_token.value().val);
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
	auto curr_token = get_next_token();
	while (curr_token.has_value() && (curr_token.value().val == "int" || curr_token.value().val == "float")) {
		declaration();
		curr_token = get_next_token();
	}
	unput_token();
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
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("ID", curr_token.value().val);
	}
	var_declaration_prime();
	return true;
}

bool parser::var_declaration_prime() {
	cout << "var_declaration_prime" << endl;
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == ";") {
			match(";", curr_token.value().val);
		}
		else if (curr_token.value().val == "[") {
			match("[", curr_token.value().val);
			curr_token = get_next_token();
			if (curr_token.has_value()) {
				match("NUM", curr_token.value().val);
			}
			curr_token = get_next_token();
			if (curr_token.has_value()) {
				match("]", curr_token.value().val);
			}
			curr_token = get_next_token();
			if (curr_token.has_value()) {
				match(";", curr_token.value().val);
			}
		}
	}
	else {
		cout << "unput_token" << endl;
		unput_token();
	}
	return true;
}

bool parser::type_specifier() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "int") {
			match("int", curr_token.value().val);
		}
		else if (curr_token.value().val == "float") {
			match("float", curr_token.value().val);
		}
	}
	return true;
}

bool parser::params() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "void") {
			match("void", curr_token.value().val);
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
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == ",") {
			match(",", curr_token.value().val);
			param();
			param_list_prime();
		}
		else {
			unput_token();
		}
	}
	return true;
}

bool parser::param() {
	type_specifier();
	auto curr_token = get_next_token();
	match("ID", curr_token.value().val);
	param_prime();
	return true;
}
bool parser::param_prime() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "[") {
			match("[", curr_token.value().val);
			match("]", curr_token.value().val);
		}
	}
	else {
		unput_token();
	}
	return true;
}

bool parser::compound_stmt() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("{", curr_token.value().val);
		statement_list();
		match("}", curr_token.value().val);
	}
	else {
		throw SyntaxError({ "{" }, curr_token.value().val);
	}
}

bool parser::statement_list() {
	auto curr_token = get_next_token();
	while (curr_token.has_value() && (curr_token.value().val == "if" || curr_token.value().val == "while" || curr_token.value().val == "return" || curr_token.value().val == "ID" || curr_token.value().val == "{")) {
		statement();
		curr_token = get_next_token();
	}
	unput_token(); //epsilon
	return true;
}

bool parser::statement() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "if") {
			unput_token();
			selection_stmt();
		}
		else if (curr_token.value().val == "while") {
			unput_token();
			iteration_stmt();
		}
		else if (curr_token.value().val == "ID") {
			unput_token();
			assignment_stmt();
		}
		else if (curr_token.value().val == "{") {
			unput_token();
			compound_stmt();
		}
		else {
			throw SyntaxError({ "if", "while", "ID", "{" }, curr_token.value().val);
		}
	}
	else {
		throw SyntaxError({ "if", "while", "ID", "{" }, curr_token.value().val);
	}
}

bool parser::selection_stmt() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("if", curr_token.value().val);
		match("(", curr_token.value().val);
		expression();
		match(")", curr_token.value().val);
		statement();
		selection_stmt_prime();
	}
	else {
		throw SyntaxError({ "if" }, curr_token.value().val);
	}
}

bool parser::selection_stmt_prime() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "else") {
			match("else", curr_token.value().val);
			statement();
		}
		else {
			unput_token();
		}
	}
	return true;
}

bool parser::iteration_stmt() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("while", curr_token.value().val);
		match("(", curr_token.value().val);
		expression();
		match(")", curr_token.value().val);
		statement();
	}
	else {
		throw SyntaxError({ "while" }, curr_token.value().val);
	}
}

bool parser::assignment_stmt() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		var();
		match("=", curr_token.value().val);
		expression();
	}
	else {
		throw SyntaxError({ "ID" }, curr_token.value().val);
	}
}
bool parser::var() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		match("ID", curr_token.value().val);
		var_prime();
	}
	else {
		throw SyntaxError({ "ID" }, curr_token.value().val);
	}
}
bool parser::var_prime() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "[") {
			match("[", curr_token.value().val);
			expression();
			match("]", curr_token.value().val);
		}
		else {
			unput_token();
		}
	}
	return true;
}

bool parser::expression() {
	additive_expression();
	expression_prime();
	return true;
}

bool parser::expression_prime() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "<=" || curr_token.value().val == "<" || curr_token.value().val == ">" || curr_token.value().val == ">=" || curr_token.value().val == "==" || curr_token.value().val == "!=") {
			unput_token();
			relop();
			additive_expression();
		}
		else {
			unput_token();
		}
	}
	return true;
}

bool parser::relop() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "<=") {
			match("<=", curr_token.value().val);
		}
		else if (curr_token.value().val == "<") {
			match("<", curr_token.value().val);
		}
		else if (curr_token.value().val == ">") {
			match(">", curr_token.value().val);
		}
		else if (curr_token.value().val == ">=") {
			match(">=", curr_token.value().val);
		}
		else if (curr_token.value().val == "==") {
			match("==", curr_token.value().val);
		}
		else if (curr_token.value().val == "!=") {
			match("!=", curr_token.value().val);
		}
		else {
			throw SyntaxError({ "<=", "<", ">", ">=", "==", "!=" }, curr_token.value().val);
		}
	}
	else {
		throw SyntaxError({ "<=", "<", ">", ">=", "==", "!=" }, curr_token.value().val);
	}
}

bool parser::additive_expression() {
	term();
	additive_expression_prime();
	return true;
}

bool parser::additive_expression_prime() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "+" || curr_token.value().val == "-") {
			addop();
			term();
			additive_expression_prime();
		}
		else {
			unput_token();
		}
	}
	return true;
}

bool parser::addop() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "+") {
			match("+", curr_token.value().val);
		}
		else if (curr_token.value().val == "-") {
			match("-", curr_token.value().val);
		}
		else {
			throw SyntaxError({ "+", "-" }, curr_token.value().val);
		}
	}
	else {
		throw SyntaxError({ "+", "-" }, curr_token.value().val);
	}
}

bool parser::term() {
	factor();
	term_prime();
	return true;
}

bool parser::term_prime() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "*" || curr_token.value().val == "/") {
			mulop();
			factor();
			term_prime();
		}
		else {
			unput_token();
		}
	}
	return true;
}

bool parser::mulop() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "*") {
			match("*", curr_token.value().val);
		}
		else if (curr_token.value().val == "/") {
			match("/", curr_token.value().val);
		}
		else {
			throw SyntaxError({ "*", "/" }, curr_token.value().val);
		}
	}
	else {
		throw SyntaxError({ "*", "/" }, curr_token.value().val);
	}
}

bool parser::factor() {
	auto curr_token = get_next_token();
	if (curr_token.has_value()) {
		if (curr_token.value().val == "(") {
			match("(", curr_token.value().val);
			expression();
			match(")", curr_token.value().val);
		}
		else if (curr_token.value().val == "ID") {
			unput_token();
			var();
		}
		else if (curr_token.value().val == "NUM") {
			match("NUM", curr_token.value().val);
		}
		else {
			throw SyntaxError({ "(", "ID", "NUM" }, curr_token.value().val);
		}
	}
	else {
		throw SyntaxError({ "(", "ID", "NUM" }, curr_token.value().val);
	}
}
