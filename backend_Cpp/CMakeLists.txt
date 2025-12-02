cmake_minimum_required(VERSION 3.15)
project(MarketScraper)

set(CMAKE_CXX_STANDARD 17)

# 1. Setup FetchContent to download 'cpr' (HTTP Library)
include(FetchContent)
FetchContent_Declare(
    cpr
    GIT_REPOSITORY https://github.com/libcpr/cpr.git
    GIT_TAG 1.10.4  # Specific version for stability
)
FetchContent_MakeAvailable(cpr)

# 2. Define our executable
add_executable(scraper_engine src/main.cpp)

# 3. Link the library to our executable
# This tells the compiler: "Let scraper_engine use cpr"
target_link_libraries(scraper_engine PRIVATE cpr::cpr)

