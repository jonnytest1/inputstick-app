
from typing import Callable


class Observer:
    def update(self, subject: "Subject"):
        """Receive update from the subject."""
        pass


class Subject:
    def __init__(self):
        self._observers: list[Observer] = []  # List of observers

    def attach(self, observer: Observer):
        """Attach an observer to the subject."""
        self._observers.append(observer)

    def on_emit(self, fnc: "Callable[[Subject],None]"):

        class OImple(Observer):
            def update(self, subject: "Subject"):
                fnc(subject)
        self.attach(OImple())

    def detach(self, observer: Observer):
        """Detach an observer from the subject."""
        self._observers.remove(observer)

    def notify(self):
        """Notify all observers of a change."""
        for observer in self._observers:
            observer.update(self)


class ConcreteSubject(Subject):
    def __init__(self):
        super().__init__()
        self._state = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.notify()  # Notify observers whenever the state changes

    def update(self, value):
        self._state = value
        self.notify()  # Notify observers whenever the state changes
