# Authentication

This is the repository for the Auth-domain - a part of [Energy Origin](https://github.com/Energinet-DataHub/energy-origin).

To support authentication in the system, a few features are necessary:

- Allow privates and professionals to log in using MitID or NemID
- Issue tokens to clients when authenticating
- Translate issued tokens into an identity with certain privileges

## OpenID Connect

The system uses [OpenID Connect](https://openid.net/connect/) to provide
identities for authentication. Users log in via an Identity Provider, who
issue a token to the system. The system in turn issue a token to the client.

It currently uses [Signaturgruppen](https://www.signaturgruppen.dk/),
who provides NemID and MitID authentication, but the current setup could be moved
to another OpenID Connect provider without changing much in the implementation.

It is planned to used OpenID Connect to authorize Energinet employees via
Azure AD in the future.

## Reusability across applications

It is advantageous if the authentication and authorization mechanisms can be
reused across different applications. Imaging, for example, Energinet has two
different applications, both depending on the same authentication features.
Being able to reuse the implementation saves us from developing and testing
duplicate functionality.

To counter this demand, the [Auth service](https://github.com/Energinet-DataHub/eo-auth),
although currently an integrated part of the system, is being designed from the
ground up to work as an independent service outside the system itself, so that
it may be deployed on its own in the future. It does this by exposing an HTTP
REST API to initiate a login flow, then performs a series of HTTP redirects,
ultimately returning the client to its desired return-URL (accompanied by a
token in case of a successful login).

# Applications

An authorization flow is divided into three different applications.

- Application Frontend is the application that wants to authorize a user
- Auth API is the backend (providing the authorization features)
- Auth frontend implements a few auth specific views, and could be the same
  as Application Frontend

## Application Frontend

The Application Frontend is the application which initiates an authorization-flow
and expects the client to return at some point - either as a logged-in user,
or as anonymous.

The Application Frontend starts by invoking an endpoint on the Auth API,
providing the `fe_url` and `return_url` parameters, and gets back an absolute
URL to initiate an authorization flow. By following this URL, the client
undergoes the entire authenticate/authorize flow before returning to `return_url`.

- `fe_url` is the base URL of the Auth frontend
- `return_url` is the URL to return the client to once the authorization flow completes
  (this would typically be a sub-path on the Application Frontend itself)

Upon returning to the Application Frontend, a few parameters are passed as
query strings, describing the outcome of the authorization flow
(succeeded/failed), and in case of failure, a reason hereof.

Upon successful authorization flow, the backend sets an HTTP cookie on the
client containing an authorization token, which the frontend can not access
directly (Secure, SameSite=Strict, HttpOnly).

## Auth API

The Auth API encapsulates the entire authorization flow, thus removing all
control logic from the Application Frontend. Once the Application Frontend
initiates an authorization flow, the client leaves the Application Frontend
and does not return until authorization either succeeded or failed.

## Auth frontend

The Auth Frontend is set of views (URLs) specific to the authorization flow,
and are thus isolated from the Application Frontend (however, these views
could be implemented on the Application Frontend as well).

An example of a view is
one where the user accepts or declines Terms & Conditions. Another example is
an onboarding-formular, where the user enters necessary details before signing
up. These views must be implemented as sub-paths to the absolute URL provided
by the Application Frontend as `fe_url` upon initiating an authorization flow.

The necessary sub-paths to support the authorization flow are:

- **/terms** allows the user to read and accept (or decline) Terms & Conditions

  - Receives query parameters `state`, `terms_url`, and `terms_accept_url`
  - Makes an HTTP GET request to `terms_url` to fetch the latest Terms & Conditions (headline, text, and version)
  - Makes an HTTP POST request to `terms_accept_url` to confirm that the user either accepted or declined the Terms & Conditions along with the version
  - After accepting or declining terms, the API returns a `next_url` where the client should be redirected to continue the authorization flow

- **/onboard** allows the user to provide necessary/additional information, such as name, e-mail etc.
  - _TODO: Coming in a future version_

# Authorization Flow
Information and diagrams explaining the authorization flow can be found [here](doc/authorization_flow.md)

# Building and running service
Information about building and running this service can be found [here](doc/running_service.md)

# Service configuration
All service configuration and environment variable can be found [here](doc/configuration.md).

# Development environment
Instruction about how to setup a development environment or see the specific requirement go [here](doc/contrib/shared/README.md).

# Workflows
All workflows is described [here](.github/workflows/README.md).
