from typing import Callable, Generic, TypeVar, Any

# A type variable to represent the callable signature of the event.
# This allows for type hinting on the callback function.
Callback = TypeVar("Callback", bound=Callable[..., Any])


class Event(Generic[Callback]):
    """
    A simple, standalone event implementation with subscribe and dispatch methods.

    This class allows for a "one-to-many" communication pattern where a single event
    can notify multiple listeners (subscribers) that an action has occurred.

    The generic type `Callback` allows the event to be type-hinted with the
    specific signature of the functions it will dispatch to, ensuring type safety.
    """

    def __init__(self):
        # A list to store the subscribed callback functions.
        self._callbacks: list[Callback] = []

    def subscribe(self, callback: Callback) -> None:
        """
        Subscribes a callback to the event.

        Args:
            callback: The function to be called when the event is dispatched.
                      Its signature should match the event's generic type.
        """
        self._callbacks.append(callback)

    def unsubscribe(self, callback: Callback) -> None:
        """
        Unsubscribes a previously subscribed callback from the event.

        Args:
            callback: The function to be removed from the event's subscribers.
        """
        self._callbacks.remove(callback)

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        """
        Dispatches the event, calling all subscribed callbacks with the given arguments.

        Args:
            *args: Variable positional arguments to pass to the callbacks.
            **kwargs: Variable keyword arguments to pass to the callbacks.
        """
        for callback in self._callbacks:
            callback(*args, **kwargs)

    def event_listener(self, callback: Callback) -> Callback:
        """
        Decorator to subscribe a function to the event. This is a convenience method.
        It still ensure static type checking on the decorated function.

        **NOTE**: it is possible to unsubscribe the function later using `event.unsubscribe(handler)`.

        Usage:
            @event.subscriber
            def handler(...): ...
        """
        self.subscribe(callback)
        return callback


# =============================================================================
# Entry point + example usage
# =============================================================================


def main() -> None:
    from typing import Protocol

    # We can define the expected function signature using a Protocol for clarity.
    class UserLoginCallback(Protocol):
        def __call__(self, username: str, user_id: int) -> None: ...

    # Create an instance of our Event, typed with the protocol.
    on_user_login = Event[UserLoginCallback]()

    def welcome_user(username: str, user_id: int) -> None:
        print(f"Welcome, {username}! Your user ID is {user_id}.")

    def log_login_event(username: str, user_id: float) -> None:
        print(f"[{username}] logged in with ID [{user_id}] at the database level.")

    # Subscribe the functions
    on_user_login.subscribe(welcome_user)
    on_user_login.subscribe(log_login_event)

    # Dispatch the event
    print("Dispatching event for user 'Alice'...")
    on_user_login.dispatch("Alice", "ddd")


if __name__ == "__main__":
    main()
