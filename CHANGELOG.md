# Changelog

All notable changes to the Houdini Swap Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive error handling examples in README
- Enhanced docstrings with exceptions, edge cases, side effects, thread safety, and performance documentation
- Defensive copying for params dicts to prevent mutation

### Fixed
- Added defensive copying in `_request()` method to prevent mutation of caller's dictionaries
- Enhanced all method docstrings with comprehensive documentation

## [0.1.0] - 2025-12-23

### Added
- Initial release of Houdini Swap Python SDK
- 100% API endpoint coverage (12 endpoints)
- Type-safe data models for all API responses
- Comprehensive exception handling
- Full type hints throughout the codebase
- Complete API documentation and examples

### Features
- Token Information APIs (CEX and DEX tokens)
- Quote APIs (CEX and DEX quotes)
- Exchange Execution APIs (CEX and DEX exchanges)
- DEX Transaction Management APIs (approve and confirm)
- Status and Information APIs (status, min-max, volume, weekly volume)

