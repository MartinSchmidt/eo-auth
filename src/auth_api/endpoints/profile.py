# Standard Library
from dataclasses import dataclass, field
from typing import List, Optional

# First party
from origin.api import Context, Endpoint


@dataclass
class UserProfile:
    """User profile information."""

    id: str
    name: str
    scope: List[str] = field(default_factory=list)
    company: Optional[str] = field(default=None)


class GetProfile(Endpoint):
    """Endpoint to get the user's (actor's) profile."""

    @dataclass
    class Response:
        """Response containing UserProfile on success."""

        success: bool
        profile: UserProfile

    def handle_request(
            self,
            context: Context
    ) -> Response:
        """
        Handle HTTP request.

        :param context: Context for a single HTTP request.
        :return: The response with the user profile
        """
        return self.Response(
            success=True,
            profile=UserProfile(
                id=context.token.actor,
                name='John Doe',
                company='New Company',
                scope=context.token.scope,
            ),
        )
