# Changelog

All notable changes to this project will be documented in this file.  
This format follows [Keep a Changelog](https://keepachangelog.com/).  
This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Description of new features or functionalities.

### Changed
- Updates or modifications to existing features.

### Fixed
- Bug fixes or issues resolved.

### Removed
- Deprecated or removed features.

---

## [0.1.0] - 28-12-2024

### Added
- `/auth/token` => Login endpoint implemented, user can authenticate to get Bearer and Refresh token.
- `/auth/register` => Register endpoint allowing user creation with validation.
- `/auth/refresh` => Token refresh endpoint, enables issuing new bearer tokens using valid refresh token.

### Features
- Full support for Bearer token authentication.
- Secure refresh token handling to maintain session continuity.
- JWT-based authentication for improved security and scalability.
