from django.db import models
import string
import re

DIGITS = list(string.digits)
NAME_CHARACTERS = list(string.ascii_letters) + ['-']
PASSWORD_CHARACTERS = list(string.ascii_letters) + list(string.digits) + ['_', '-']
SUBJECT_CHARACTERS = list(string.ascii_letters) + list(string.digits) + ['_', '-'] + [' ']
EMAIL_PATTERN = re.compile("^[a-zA-Z0-9\._]+[@]+([a-zA-Z0-9\._]*)+[a-zA-Z0-9]+[.]\w{2,4}$")
TIME_PATTERN = re.compile("^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=30)

    @staticmethod
    def authenticate(email, password):
        query = User.objects.filter(email=email, password=password)
        return query[0] if query else None

    @staticmethod
    def check_user(email, password):
        query = User.objects.filter(email=email, password=password)
        if not query:
            return False, "Zły email lub hasło."
        return True, ""

    @staticmethod
    def check_first_name(name):
        if not 0 < len(name) <= 30:
            return False, "Niepoprawna długość imienia (od 1 do 30)."
        if any(c not in NAME_CHARACTERS for c in name):
            return False, "Niepoprawne znaki w imieniu (dopuszczalne: a-z, A-Z, '-')."
        return True, ""

    @staticmethod
    def check_last_name(name):
        if not 0 < len(name) <= 30:
            return False, "Niepoprawna długość nazwiska (od 1 do 30)."
        if any(c not in NAME_CHARACTERS for c in name):
            return False, "Niepoprawne znaki w nazwisku (dopuszczalne: a-z, A-Z, '-')."
        return True, ""

    @staticmethod
    def check_new_password(password):
        if not 8 <= len(password) <= 30:
            return False, "Niepoprawna długość hasła (od 8 do 30)."
        if not any(c in string.ascii_uppercase for c in password):
            return False, "Hasło musi zawierać conajmniej jeden duży znak (A-Z)."
        if not any(c in string.ascii_lowercase for c in password):
            return False, "Hasło musi zawierać conajmniej jeden mały znak (a-z)."
        if not any(c in string.digits for c in password):
            return False, "Hasło musi zawierać conajmniej jedną cyfrę (0-9)."
        if any(c not in PASSWORD_CHARACTERS for c in password):
            return False, "Niepoprawne znaki w haśle (dopuszczalne: a-z, A-Z, 0-9, '_', '-')."
        return True, ""

    @staticmethod
    def check_both_passwords(password, repeated_password):
        if password != repeated_password:
            return False, "Podane hasła były różne."
        return True, ""

    @staticmethod
    def check_email(email):
        if not re.match(pattern=EMAIL_PATTERN, string=email):
            return False, "Niepoprawy format adresu email."
        query = User.objects.filter(email=email)
        if query:
            return False, "Email został już wcześniej użyty."
        return True, ""

    @staticmethod
    def check_remind_email(email):
        query = User.objects.filter(email=email)
        if not query:
            return False, "Nieistniejący email w bazie aNote."
        return True, ""

    @staticmethod
    def get_password(email):
        query = User.objects.filter(email=email)
        return query[0].password

    def change_password(self, new_password):
        self.password = new_password
        self.save()


class Authorized(User):
    @staticmethod
    def authenticate(email, password):
        query = Authorized.objects.filter(email=email, password=password)
        return query[0] if query else None


class Subject(models.Model):
    name = models.CharField(max_length=30, unique=True)

    @staticmethod
    def check_name(name):
        if not 0 < len(name) <= 30:
            return False, "Niepoprawna długość nazwy przedmiotu (od 1 do 30)"
        if any(c not in SUBJECT_CHARACTERS for c in name):
            return False, "Niepoprawne znaki w nazwie przedmiotu (dopuszczalne: a-z, A-Z, 0-9, '_', '-', ' ')."
        query = Subject.objects.filter(name=name)
        if query:
            return False, "Przedmiot o takiej nazwie już istnieje."
        return True, ""

    @staticmethod
    def name_exists(name):
        query = Subject.objects.filter(name=name)
        return True if query else False

    @staticmethod
    def get_subject_by_name(name):
        query = Subject.objects.filter(name=name)
        return query[0] if query else None


CLASSES_TYPE = [
    ('EXE', 'Ćwiczenia'),
    ('LAB', 'Laboratorium'),
    ('LEC', 'Wykład'),
    ('SEM', 'Seminarium')
]


class Classes(models.Model):
    classes_type = models.CharField(max_length=3, choices=CLASSES_TYPE)
    group_number = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    authorized = models.ForeignKey(Authorized, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def is_user_a_creator_of_class(self, user):
        return user.email == self.authorized.email

    @staticmethod
    def check_date(date):
        if date == "":
            return False, "Proszę podać datę."
        return True, ""

    # @staticmethod
    # def check_classes_type(classes_type):
    #     if classes_type is None:
    #         return False, "Proszę zaznaczyć typ zajęć."
    #     return True, ""

    @staticmethod
    def check_group_number(group_number):
        if group_number == "" or any(c not in DIGITS for c in group_number) or group_number[0] == '0':
            return False, "Podany numer grupy ma być dodatnią liczbą całkowitą."
        return True, ""

    @staticmethod
    def check_time(time):
        if not re.match(pattern=TIME_PATTERN, string=time):
            return False, "Oczekiwany format HH:MM 24-godzinny z zerem wiodącym."
        return True, ""

    @staticmethod
    def check_times(start_time, end_time):
        if not start_time <= end_time:
            return False, "Czas rozpoczęcia nie powinien być późniejszy niż zakończenia."
        return True, ""

    @staticmethod
    def check_subject(subject):
        if not Subject.name_exists(subject):
            return False, "Przedmiot o podanej nazwie nie istnieje."
        return True, ""

    @staticmethod
    def get_class_by_id(classes_id):
        query = Classes.objects.filter(id=classes_id)
        return query[0] if query else None


TEXT_STYLE = [
    ('LTX', 'Latex'),
    ('MD', 'Markdown'),
    ('TXT', 'Text')
]


class Note(models.Model):
    STATE = [
        ('U', 'Niezadeklarowane'),
        ('D', 'Zadeklarowane'),
        ('F', 'Skończone')
    ]
    state = models.CharField(max_length=1, choices=STATE, default="U")
    text_style = models.CharField(max_length=3, choices=TEXT_STYLE, default="TXT")
    contents = models.TextField(default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    classes = models.OneToOneField(Classes, on_delete=models.CASCADE)

    @staticmethod
    def get_note_by_classes(classes):
        query = Note.objects.filter(classes=classes)
        return query[0] if query else None


class Correction(models.Model):
    text_style = models.CharField(max_length=3, choices=TEXT_STYLE)
    contents = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)

    @staticmethod
    def get_correction_by_id(id):
        query = Correction.objects.filter(id=id)
        return query[0] if query else None


class Observation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group_number = models.IntegerField()
    classes_type = models.CharField(max_length=3, choices=CLASSES_TYPE)

    @staticmethod
    def check_observation(user, subject, group_number, classes_type):
        group_number = int(group_number)
        query = Observation.objects.filter(user=user, subject=subject, group_number=group_number,
                                           classes_type=classes_type)
        if query:
            return False, "Już obserwujesz taką grupę."
        return True, ""

    class Meta:
        unique_together = ('user', 'subject', 'group_number', 'classes_type')
