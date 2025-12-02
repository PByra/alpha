#include <iostream>
#include <cpr/cpr.h> //libary for HTTP requests

int main() {
    // Testing free api 
    std::string apiKey = "kKfabUuMJgXb3K6NGEzm5zNwNfzvVLok"; 
    std::string symbol = "AAPL";
    std::string url = "https://financialmodelingprep.com/api/v3/profile/" + symbol + "?apikey=" + apiKey;

    std::cout << "Fetching data for " << symbol << "..." << std::endl;

    cpr::Response r = cpr::Get(cpr::Url{url});

    if (r.status_code == 200) {
        std::cout << "--- SUCCESS ---" << std::endl;
        std::cout << r.text << std::endl; // Print the raw JSON
    } else {
        std::cout << "--- ERROR ---" << std::endl;
        std::cout << "Status Code: " << r.status_code << std::endl;
        std::cout << "Message: " << r.error.message << std::endl;
    }

    return 0;
}

