# Authorization flow

The authorization flow is implemented as a set of HTTP redirects back and
forth between the three systems. It only supports browser authentication.

## State

During redirects between Auth API and other systems, you will notice a `state`
object is being passed back and forth. It contains all data collected during
the entire authorization flow, and exists so that Auth API can be stateless.
It is a signed JWT containing all data, so only Auth API can edit its content.

## Sequence diagram

### Login flow

![alt text](/doc/diagrams/login-flow.drawio.png)

### Logout flow

![alt text](/doc/diagrams/logout-flow.drawio.png)


# Tokens

Upon successful authorization, the Auth API creates two tokens representing
the user; An internal token containing all necessary details about the user,
and an opaque token which refers to the internal token, but does not contain
any data in itself (it is a random generated UUID4).

The opaque token is set as an HTTP Cookie on the Auth API's domain, so that
subsequent requests to the API includes the token automatically. The client
never gets access to the internal token.

Once requests hit the API, an API Gateway (Træfik) translates the opaque token
into the internal token using a [ForwardAuth endpoint](https://doc.traefik.io/traefik/v2.0/middlewares/forwardauth/),
and then forwards the requests to the appropriate service. Thus, from the
perspective of a service, only the internal token exists (and is relevant).

TODO Internal token is JWT

## Actor vs. Subject

An important distinction to make is the difference between an _Actor_ and a
_Subject_.

Internal tokens contains both `actor` and `subject` field:

- The `actor` describes the user doing the action, and will contain the unique
  ID of the user who authenticated.
- The `subject` describes _who_ the action were done on behalf of.

This allows issuing tokens and invoking the API on behalf of someone else. For
example, if _John_ acts on behalf of _Lisa_, the `actor` would be _John_, and
the `subject` would be _Lisa_. Thus John would have access to all of Lisa's data,
however, any action made by John can be tracked back to him.

## Scopes

Tokens are always issued with a list of scopes. They determine which privileges
a client has when making requests to the API. When authenticating as one self
(ie. not working on behalf of someone else), the token would contain all
scopes necessary to access and mutate one's own data. When working on behalf
of someone else, the token could contain a limited set of scopes.

Examples of scopes:

- `meteringpoints.read`
- `measurements.read`
- etc.

TODO List all possible scopes?

## Interpreting opaque tokens

The sequence diagram below illustrates the flow of incoming requests to the
API, and how the opaque token is translated into an internal token before
being routed to the service.

- Client makes a request to the API's public URL, which is routed to the API Gateway
- The API Gateway invokes a [ForwardAuth endpoint](https://doc.traefik.io/traefik/v2.0/middlewares/forwardauth/)
  on the Auth API (forwarding the client's original request)
- The Auth API reads the opaque token from an HTTP cookie, and queries a simple
  key-value database for an internal token.
- If the token exists and is valid, the ForwardAuth endpoint returns an HTTP
  200 OK along with the internal token in the _Authorization_ response header
  - The request is forwarded to the service containing the _Authorization_
    request header
- Otherwise, an HTTP 401 Unauthorized is returned to the client, stopping
  further processing of the request

![alt text](/doc/diagrams/forwardauth-flow.drawio.png)

## Internal tokens

As illustrated it the diagram above, services only have to concern itself with
the internal token. It contains all necessary data for services to decide
whether a request is properly authorized. The internal token is a JWT signed
by Auth API.

An example of an internal token:

```json
{
  "name": "John Doe",
  "company": "John's Fine Wine",
  "issued": "2021-12-22 13:50:20+00:00",
  "expires": "2022-01-22 13:50:20+00:00",
  "actor": "33785eeb-2527-4e43-b091-8496af1972b0",
  "subject": "1f71a97b-a207-47b5-a5bf-0bd1006245d4",
  "scope": ["meteringpoints.read", "measurements.read"]
}
```

# Frontend security policies

To ensure strict and secure communication between our frontend applications and
the Auth API, we use HTTPS with strict Content Security Policy and CORS policy.
The authorization cookie set by the Auth API uses the `HttpOnly`, `Secure`, and
`SameSite=Strict` flags in non-development environments.

To allow local frontend development against remote development environments, the
authorization cookie is sent to the client (no `HttpOnly` flag) with
`SameSite=None`. The `Secure` flag is support by requests from a `localhost`
origin. HTTP clients must forward credentials with every request except for the
OIDC login endpoint. This requires the Auth API to respond with an
`Access-Control-Allow-Credentials: true` header. Requests from the
`http://localhost:4200` origin are allowed by responding with an
`Access-Control-Allow-Origin: http://localhost:4200` header.
