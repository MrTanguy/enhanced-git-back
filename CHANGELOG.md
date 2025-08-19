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

## [1.0.0] - 19-08-2025

### Added
- Continuous Integration (CI) and Continuous Deployment (CD) pipeline.
- New deployment files: `Dockerfile.[preprod/prod]` and `docker-compose.[preprod/prod].yml`.
- Full integration of `gitlab.py` module for GitLab API connections and requests.
- Unit tests covering GitLab-related functionalities.
- A liveness and logless route `/heath`

### Changed
- Database adjustments to support new features (migrations and minor schema updates).
- OAuth connection now includes **scope verification** for enhanced permission control.
- Improved token security with stronger encryption mechanisms.

### Fixed
- Issues with GitLab OAuth token refresh reliability.
- Minor fixes in Docker configuration and Traefik compatibility.

---

## [0.5.0] - 30-07-2025

### Added 
 - `alembic` : create and manage migrations.
 - `.github/workflow/CI.yml` : CI that run TU and PyLint.
 -  `/tests/repositories` added tests to improve code coverage to 96%.
 - `/user/me` : return the user ID.

### Changed 
 - A lot of files to respect PyLint recommendations.

--- 

## [0.4.0] - 16-07-2025

### Added
- `get_all_public_projects` function in `services/oauth/github` for fetching public GitHub projects.
- Input validation using Pydantic models for portfolio data.
- Extensive test suite with 74% code coverage.
- Implemented `read` method on `ConnectionRepository`.

### Changed
- Refactored application structure: moved source files from `api/` to `routers/`.
- Updated `Dockerfile` to reflect new project structure and dependencies.
- `routers/connection` : adding a new `/projets` route, returning all public projects.

### Fixed
- Bug fixes and improvements on the `PortfolioRepository` CRUD implementation.

---

## [0.3.0] - 31-03-2025

### Changed 
- New way to verify the bearer token (Annotated)
- New DB models to manage portfolios (portfolio, portfolio_connection, user.portfolios)

### Added
- Unit tests for `/`, `/auth` and `/connection`
- `/portfolio` => New subroute for portfolio related routes
- `/portfolio/create` => Create a new portfolio for the user
- `/portfolio/{portfolio_ulid}` => Give all the informations about the portfolio

### Featured
- First functions to use portfolio (many more to come)

---

## [0.2.0] - 03-02-2025

### Changed 
- There are now 3 subroutes : /auth, /connect, /user

### Added
- `/connect/url` => Endpoint to get the oauth url of the asked website.
- `/connect/token` => Callback endpoint to connect a user with a Connection (only github at that moment).
- `/connect/delete` => Delete a user's Connection.
- `/user/data` => Endpoint that give all the Connection informations about the user

### Featured
- The Oauth connection can be implemented with the abstract OauthInterface (Github is fully implement)

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
