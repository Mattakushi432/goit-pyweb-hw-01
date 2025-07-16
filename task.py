import pickle
from collections import UserDict
from datetime import datetime, date, timedelta
from abc import ABC, abstractmethod


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number: str):
        self.phones.append(Phone(phone_number))

    def add_birthday(self, birthday_str: str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                b_date = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                b_this_year = b_date.replace(year=today.year)
                if b_this_year < today:
                    b_this_year = b_this_year.replace(year=today.year + 1)
                if 0 <= (b_this_year - today).days < 7:
                    if b_this_year.weekday() >= 5:
                        b_this_year += timedelta(days=7 - b_this_year.weekday())
                    upcoming.append(
                        {"name": record.name.value, "congratulation_date": b_this_year.strftime("%d.%m.%Y")})
        return upcoming


class AbstractView(ABC):
    @abstractmethod
    def display_message(self, message):
        pass

    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_birthdays(self, birthdays):
        pass


class ConsoleView(AbstractView):
    def display_message(self, message):
        print(message)

    def display_contacts(self, contacts):
        if not contacts:
            self.display_message("No contacts found.")
        else:
            for record in contacts:
                self.display_message(str(record))

    def display_birthdays(self, birthdays):
        if not birthdays:
            self.display_message("No upcoming birthdays.")
        else:
            for entry in birthdays:
                self.display_message(f"{entry['name']}: {entry['congratulation_date']}")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError, AttributeError) as e:
            return f"Error: {e}"

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return "Contact added/updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return record


@input_error
def show_all(book: AddressBook):
    return list(book.data.values())


@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()


def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), *args


def main():
    book = AddressBook()
    view = ConsoleView()

    view.display_message("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            view.display_message("Good bye!")
            # Тут може бути save_data(book)
            break
        elif command == "hello":
            view.display_message("How can I help you?")
        elif command == "add":
            message = add_contact(args, book)
            view.display_message(message)
        elif command == "phone":
            result = show_phone(args, book)
            if isinstance(result, Record):
                view.display_contacts([result])
            else:
                view.display_message(result)
        elif command == "all":
            all_contacts = show_all(book)
            view.display_contacts(all_contacts)
        elif command == "birthdays":
            upcoming_birthdays = birthdays(book)
            view.display_birthdays(upcoming_birthdays)
        # ... (додати інші команди аналогічно)
        else:
            view.display_message("Invalid command.")


if __name__ == "__main__":
    main()
