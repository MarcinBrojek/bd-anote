from django.shortcuts import render, redirect
from .models import User, Authorized, Subject, Classes, Observation, Note, Correction
from django.core.mail import send_mail
from datetime import datetime
from django.http import HttpResponseNotFound, Http404, HttpResponse
from django_tex.shortcuts import render_to_pdf
import mimetypes
from django.db.models import Q

def checker(funcs, args):
    signal = ""
    msg = ""
    for fun, arg in zip(funcs, args):
        signal, msg = fun(*arg)
        if not signal:
            return signal, msg
    return signal, msg


def login(request):
    if request.method == 'POST':
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")

        funcs = [User.check_user]
        args = [[email, password]]
        signal, msg = checker(funcs, args)
        if not signal:
            return render(request, 'login.html', context={'info': msg})

        request.session['email'] = email
        request.session['password'] = password
        return redirect('profile')
    else:
        info = request.session.get('info')
        if info is not None:
            del request.session['info']
            request.session.modified = True
        context = {'info': info} if info else None
        return render(request, 'login.html', context=context)


def check_session_user(request):
    email = request.session.get('email', None)
    password = request.session.get('password', None)
    if email is None or password is None:
        request.session['info'] = "Sesja wygasła."
        return redirect('login'), None

    user = User.authenticate(email=email, password=password)
    if user is None:
        request.session['info'] = "Ups. Coś poszło nie tak."
        return redirect('login'), None

    return None, user


def check_session_authorized(request):
    email = request.session.get('email', None)
    password = request.session.get('password', None)
    if email is None or password is None:
        request.session['info'] = "Sesja wygasła."
        return redirect('login'), None

    authorized = Authorized.authenticate(email=email, password=password)
    if authorized is None:
        request.session['info'] = "Ups. Coś poszło nie tak."
        return redirect('login'), None

    return None, authorized


def logout(request):
    request.session.flush()
    request.session['info'] = "Pomyślnie wylogowano."
    return redirect('login')


def profile(request, context=None):
    email = request.session.get('email', None)
    password = request.session.get('password', None)

    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    authorized = bool(Authorized.authenticate(email=user.email, password=user.password))

    context = {
        'name': f"{user.first_name} {user.last_name}",
        'authorized': authorized,
    }
    return render(request, 'profile.html', context=context)


def remind(request):
    if request.method == 'POST':
        email = request.POST.get("email", "")

        funcs = [User.check_remind_email]
        args = [[email]]
        signal, msg = checker(funcs, args)
        if not signal:
            return render(request, 'remind.html', context={'info': msg})

        subject = 'Twoje hasło do konta w aNote.'
        message = 'Zgodnie z Twoją prośbą przesyłamy na email hasło do konta w aNote: ' + User.get_password(email)
        send_mail(subject=subject, message=message, from_email='aNote.info@gmail.com', recipient_list=[email])
        return render(request, 'login.html',
                      context={'info': f"Hasło zostało wysłane na skrzynkę pocztową {email}."})
    else:
        return render(request, 'remind.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name", None)
        last_name = request.POST.get("last_name", None)
        email = request.POST.get("email", None)
        password = request.POST.get("password", None)
        repeated_password = request.POST.get("repeated_password", None)

        context = {'first_name': first_name, 'last_name': last_name, 'email': email}

        funcs = [User.check_first_name, User.check_last_name, User.check_email, User.check_new_password,
                 User.check_both_passwords]
        args = [[first_name], [last_name], [email], [password], [password, repeated_password]]
        signal, msg = checker(funcs, args)
        if not signal:
            context['info'] = msg
            return render(request, 'register.html', context)

        request.session['email'] = email
        request.session['password'] = password
        User(first_name=first_name, last_name=last_name, password=password, email=email).save()
        return redirect('profile')
    else:
        context = {'first_name': "", 'last_name': "", 'email': ""}
        return render(request, 'register.html', context=context)


def change(request):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    if request.method == 'POST':
        old_password = request.POST.get("old_password", None)
        new_password = request.POST.get("new_password", None)
        repeated_new_password = request.POST.get("repeated_new_password", None)
        context = {}

        user = User.authenticate(email=user.email, password=old_password)
        if user is None:
            context['info'] = "Niepoprawne stare hasło."
            return render(request, 'change.html', context=context)

        funcs = [User.check_new_password, User.check_both_passwords]
        args = [[new_password], [new_password, repeated_new_password]]
        signal, msg = checker(funcs, args)
        if not signal:
            context['info'] = msg
            return render(request, 'change.html', context)

        user.change_password(new_password=new_password)
        return logout(request)
    else:
        return render(request, 'change.html')


def add_subject(request):
    failed_response, authorized = check_session_authorized(request)
    if failed_response is not None:
        return failed_response

    if request.method == 'POST':
        name = request.POST.get("name", None)
        context = {}

        funcs = [Subject.check_name]
        args = [[name]]
        signal, msg = checker(funcs, args)
        if not signal:
            context['info'] = msg
            return render(request, 'add_subject.html', context)

        context['info'] = f"Pomyślnie dodano przedmiot: {name}."
        Subject(name=name).save()
        return render(request, 'add_subject.html', context=context)
    else:
        return render(request, 'add_subject.html')


def add_classes(request):
    failed_response, authorized = check_session_authorized(request)
    if failed_response is not None:
        return failed_response

    if request.method == 'POST':
        classes_type = request.POST.get("classes_type", None)
        group_number = request.POST.get("group_number", None)
        date = request.POST.get("date", None)
        start_time = request.POST.get("start_time", None)
        end_time = request.POST.get("end_time", None)
        subject = request.POST.get("subject", None)

        context = {'classes_type': classes_type, 'group_number': group_number, 'date': date,
                   'start_time': start_time, 'end_time': end_time, 'subject': subject}

        funcs = [Classes.check_group_number, Classes.check_date, Classes.check_time, Classes.check_time,
                 Classes.check_times, Classes.check_subject]
        args = [[group_number], [date], [start_time], [end_time], [start_time, end_time], [subject]]
        signal, msg = checker(funcs, args)
        if not signal:
            context['info'] = msg
            return render(request, 'add_classes.html', context)

        start_time = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        classes_obj = Classes(classes_type=classes_type, group_number=int(group_number),
                              start_time=start_time, end_time=end_time,
                              authorized=authorized, subject=Subject.get_subject_by_name(subject))
        classes_obj.save()
        Note(classes=classes_obj).save()
        context = {'info' : "Pomyślnie dodano zajęcia."}

        return render(request, 'add_classes.html', context=context)
    else:
        return render(request, 'add_classes.html')


def classes(request):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    if request.method == 'POST':
        subject = request.POST.get("subject", None)
        date = request.POST.get("date", None)
        classes_type = request.POST.get("classes_type", None)
        group_number = request.POST.get("group_number", None)
        is_watched = request.POST.get("is_watched", None)

        context = {'classes_type': classes_type, 'group_number': group_number, 'date': date, 'subject': subject,
                   'is_watched': is_watched}

        result = Classes.objects
        if subject != "" and subject is not None:
            result = result.filter(subject__name=subject)
        if date != "" and date is not None:
            date = datetime.strptime(date, "%Y-%m-%d")
            result = result.filter(start_time__year=date.year, start_time__month=date.month, start_time__day=date.day)
        if classes_type != "" and classes_type is not None:
            result = result.filter(classes_type=classes_type)
        if group_number != "" and group_number is not None:
            group_number = int(group_number)
            result = result.filter(group_number=group_number)

        watched_classes = []
        if is_watched == "TAK":
            watched_list = Observation.objects.filter(user=user) or []
            for watched in watched_list:
                watched_classes += list(result.filter(subject=watched.subject, group_number=watched.group_number,
                                                      classes_type=watched.classes_type))
        else:
            watched_classes = list(result.all()) or []

        context['filtered_classes'] = watched_classes
        return render(request, 'classes.html', context=context)
    else:
        return render(request, 'classes.html')


def watched(request):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    if request.method == 'GET':
        watched_list = list(Observation.objects.filter(user=user))
        context = {'watched_list': watched_list}
        return render(request, 'watched.html', context)

    else:
        watched_list = list(Observation.objects.filter(user=user))
        subject = request.POST.get("subject")
        classes_type = request.POST.get("classes_type")
        group_number = request.POST.get("group_number")

        context = {'watched_list': watched_list, 'subject': subject, 'classes_type': classes_type,
                   'group_number': group_number}

        funcs = [Classes.check_subject, Classes.check_group_number, Observation.check_observation]
        args = [[subject], [group_number],
                [user, Subject.get_subject_by_name(subject), group_number, classes_type]]

        signal, msg = checker(funcs, args)
        if not signal:
            context['info'] = msg
            return render(request, 'watched.html', context)

        context['info'] = "Dodano do obserwowanych."
        Observation(user=user, subject=Subject.get_subject_by_name(subject), group_number=group_number,
                    classes_type=classes_type).save()
        context['watched_list'] = list(Observation.objects.filter(user=user))
        return render(request, 'watched.html', context)


def watched_remove(request, observ_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response
    
    watched_obj = Observation.objects.filter(user=user, id=observ_id)
    if len(watched_obj.all()) == 0:
        return HttpResponseNotFound("<h1>Nie znaleziono grupy.</h1>")
    
    watched_obj[0].delete()
    return redirect('watched')


def is_class_creator(user, classes_obj):
    return classes_obj.is_user_a_creator_of_class(user)


def is_note_undeclared(note):
    return note.state == 'U'


def is_note_mine(user, note):
    return note.author == user


def class_note(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)
    state = note.state
    author = note.author
    text_style = note.text_style
    contents = note.contents
    authorized = classes_obj.authorized

    classes_type = classes_obj.classes_type
    group_number = classes_obj.group_number
    date = classes_obj.start_time.strftime("%d.%m.%Y")
    start_time = classes_obj.start_time.strftime("%H:%M")
    end_time = classes_obj.end_time.strftime("%H:%M")
    subject = classes_obj.subject.name
    email = classes_obj.authorized.email

    link_prefix = f"/profile/classes/{classes_id}/"
    edition_action = {'link': link_prefix + "edition", 'name': "edytuj"}
    publication_action = {'link': link_prefix + "publish", 'name': "opublikuj"}
    corrections_action = {'link': link_prefix + "corrections", 'name': "lista poprawek"}
    reset_action = {'link': link_prefix + "reset", 'name': "zresetuj"}
    delete_action = {'link': link_prefix + "delete", 'name': "usuń zajęcia"}
    declaration_action = {'link': link_prefix + "declare", 'name': "zadeklaruj"}
    resignation_action = {'link': link_prefix + "resign", 'name': "zrezygnuj"}
    add_correct_action = {'link': link_prefix + "correction/add", 'name': "poprawka"}

    creator_actions = [edition_action, publication_action, corrections_action, reset_action, delete_action]
    not_declared_actions = [declaration_action, add_correct_action]
    my_note_actions = [resignation_action, edition_action, publication_action, corrections_action]
    watch_note_actions = [add_correct_action]

    visibility = True
    if is_class_creator(user, classes_obj):
        actions = creator_actions
    elif is_note_undeclared(note):
        actions = not_declared_actions
    elif is_note_mine(user, note):
        actions = my_note_actions
    else:
        actions = watch_note_actions
        visibility = note.state == 'F'

    note_info = {'type': note.text_style, 'text': note.contents, 'visibility': visibility}
    actions = [(i + 1, action) for i, action in enumerate(actions)]

    context = {'classes_type': classes_type, 'group_number': group_number, 'date': date, 'start_time': start_time,
               'end_time': end_time, 'subject': subject, 'email': email, 'note_id': note.id, 'actions': actions, 'note': note_info}

    return render(request, 'class_note.html', context)


def edit_note(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, note):
        request.session['info'] = "Ups. Coś poszło nie tak."
        return redirect('profile')

    if request.method == 'POST':
        note.text_style = request.POST.get('text_style')
        note.contents = request.POST.get('contents')
        note.save()

    context = {
        'note': note,
        'date': classes_obj.start_time.strftime("%d.%m.%Y"),
        'start_time': classes_obj.start_time.strftime("%H:%M"),
        'end_time': classes_obj.end_time.strftime("%H:%M"),
        'email': classes_obj.authorized.email,
        'text_style': note.text_style,
        'contents': note.contents,
        'correction': False,
        'classes_id': classes_id,
    }

    return render(request, 'edit_note.html', context=context)


def note_corrections(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, note):
        return HttpResponseNotFound("<h1>Brak uprawnień.</h1>")

    corrections = Correction.objects.filter(note=note)
    corrections = [
        {'id': correction.id, 'author': f"{correction.author.first_name} {correction.author.last_name} {correction.author.email}"} for correction in corrections
    ]
    context = {
        'corrections': corrections,
        'classes_id': classes_id,
    }

    return render(request, 'note_corrections.html', context=context)


def accept_correction(request, classes_id, correction_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    correction_obj = Correction.get_correction_by_id(correction_id)
    if classes_obj is None or correction_obj is None:
        return HttpResponseNotFound("<h1>Zajęć lub poprawki nie znajeziono.</h1>")

    note = correction_obj.note

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, note):
        return HttpResponseNotFound("<h1>Brak uprawnień.</h1>")

    note.text_style = str(correction_obj.text_style)
    note.contents = str(correction_obj.contents)
    note.save()
    correction_obj.delete()
    return redirect('note_corrections', classes_id)


def reject_correction(request, classes_id, correction_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    correction_obj = Correction.get_correction_by_id(correction_id)
    if classes_obj is None or correction_obj is None:
        return HttpResponseNotFound("<h1>Zajęć lub poprawki nie znajeziono.</h1>")

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, correction_obj.note):
        return HttpResponseNotFound("<h1>Brak uprawnień.</h1>")

    correction_obj.delete()
    return redirect('note_corrections', classes_id)


def publish_note(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if is_class_creator(user, classes_obj) or is_note_mine(user, note):
        note.state = 'F'
        note.save()
        return redirect('class_note', classes_id)

    return HttpResponseNotFound('<h1>"Anime jest filmem." - F.M.</h1>')


def note_reset(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if is_class_creator(user, classes_obj):
        note.delete()
        note = Note(classes=classes_obj)
        note.save()
        return redirect('class_note', classes_id)

    return HttpResponseNotFound(
        '<h1>"Gdyby istniało ZOO matematyczne, zbiór Cantore\'a byłby w pierwszej klatce." - J.S.</h1>')


def class_delete(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    if is_class_creator(user, classes_obj):
        classes_obj.delete()
        return redirect('profile')

    return HttpResponseNotFound(
        '<h1>"Najwyższy Pekińczyk nie jest wyższy od najwyższego Chińczyka." - S.</h1>')


def note_declare(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if is_note_undeclared(note):
        note.state = 'D'
        note.author = user
        note.save()
        return redirect('class_note', classes_id)

    return HttpResponseNotFound('<h1>"ELYTARNY MIMUW" - E.M.</h1>')


def note_resign(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if is_note_mine(user, note):
        note.state = 'U'
        note.author = None
        note.save()
        return redirect('class_note', classes_id)

    return HttpResponseNotFound('<h1>"WOLOLOLO." - Anonymous Mage.</h1>')


def add_correction(request, classes_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    classes_obj = Classes.get_class_by_id(classes_id)
    if classes_obj is None:
        return HttpResponseNotFound("<h1>Zajęć nie znajeziono.</h1>")

    note = Note.get_note_by_classes(classes_obj)

    if is_class_creator(user, classes_obj) and is_note_mine(user, note):
        request.session['info'] = "Ups. Coś poszło nie tak."
        return redirect('profile')

    correction = Correction(text_style=note.text_style, contents=note.contents, author=user, note=note)
    correction_query = Correction.objects.filter(author=user)
    if correction_query:
        correction = correction_query[0]

    if request.method == 'POST':
        correction.text_style = request.POST.get('text_style')
        correction.contents = request.POST.get('contents')
        correction.save()

    context = {
        'note': note,
        'date': classes_obj.start_time.strftime("%d.%m.%Y"),
        'start_time': classes_obj.start_time.strftime("%H:%M"),
        'end_time': classes_obj.end_time.strftime("%H:%M"),
        'email': classes_obj.authorized.email,
        'text_style': correction.text_style,
        'contents': correction.contents,
        'correction': True,
        'classes_id': classes_id,
    }

    return render(request, 'edit_note.html', context=context)


def pdf_note(request, note_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    note_obj = Note.objects.get(id=note_id)
    if note_obj is None or note_obj.text_style != 'LTX':
        return HttpResponseNotFound("<h1>Notatki w formacie PDF nie znajeziono.</h1>")

    context = {'latexnote': note_obj.contents}
    return render_to_pdf(request, 'pdf_note.tex', context=context, filename='notatka')


def note_download(request, note_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    note_obj = Note.objects.get(id=note_id)
    if note_obj is None:
        return HttpResponseNotFound("<h1>Notatki nie znajeziono.</h1>")

    note_type = {'TXT': 'txt', 'LTX': 'tex', 'MD': 'md'}[note_obj.text_style]
    response = HttpResponse(note_obj.contents, content_type={
        'TXT': 'text/plain', 'LTX': 'text/vnd.latex-z', 'MD': 'text/markdown'
    }[note_obj.text_style])
    response['Content-Disposition'] = f"attachment; filename=notatka_{note_id}.{note_type}"
    return response


def notes(request):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response
    
    notes_obj = Note.objects.filter(Q(author=user) | Q(classes__authorized=user)).distinct()
    corrections_obj = Correction.objects.filter(author=user)

    context = {
        'notes' : [
            {
                'id': note.id,
                'classes_id': note.classes.id,
                'date': note.classes.start_time.strftime("%d.%m.%Y"),
                'start_time': note.classes.start_time.strftime("%H:%M"),
                'end_time': note.classes.end_time.strftime("%H:%M"),
                'type': note.classes.classes_type,
                'group': note.classes.group_number,
                'subject': note.classes.subject.name,
                'corr_count': len(note.correction_set.all() or set())
            } for note in notes_obj],
        'corrections' : [
            {
                'id': correction.id,
                'classes_id': correction.note.classes.id,
                'date': correction.note.classes.start_time.strftime("%d.%m.%Y"),
                'start_time': correction.note.classes.start_time.strftime("%H:%M"),
                'end_time': correction.note.classes.end_time.strftime("%H:%M"),
                'type': correction.note.classes.classes_type,
                'group': correction.note.classes.group_number,
                'subject': correction.note.classes.subject.name
            } for correction in corrections_obj]
    }

    return render(request, 'notes.html', context=context)


def correction_preview(request, classes_id, correction_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response
    
    classes_obj = Classes.objects.filter(id=classes_id)
    correction_obj = Correction.objects.filter(id=correction_id)

    if len(classes_obj.all()) != 1 or len(correction_obj.all()) != 1:
        return HttpResponseNotFound("<h1>Nieprawidłowy adres http.</h1>")

    classes_obj = classes_obj[0]
    correction_obj = correction_obj[0]
    note_obj = correction_obj.note

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, note_obj):
        return HttpResponseNotFound("<h1>Brak uprawnień.</h1>")

    classes_type = classes_obj.classes_type
    group_number = classes_obj.group_number
    date = classes_obj.start_time.strftime("%d.%m.%Y")
    start_time = classes_obj.start_time.strftime("%H:%M")
    end_time = classes_obj.end_time.strftime("%H:%M")
    subject = classes_obj.subject.name
    email = classes_obj.authorized.email

    note_info = {'type': correction_obj.text_style, 'text': correction_obj.contents, 'visibility': True}

    context = {'classes_type': classes_type, 'group_number': group_number, 'date': date, 'start_time': start_time,
        'end_time': end_time, 'subject': subject, 'email': email, 'correction_id': correction_id, 'classes_id': classes_id, 'note': note_info}

    return render(request, 'correction_preview.html', context)


def pdf_correction(request, correction_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    correction_obj = Correction.objects.filter(id=correction_id)

    if len(correction_obj.all()) != 1:
        return HttpResponseNotFound("<h1>Nieprawidłowy adres http.</h1>")

    correction_obj = correction_obj[0]
    note_obj = correction_obj.note
    classes_obj = note_obj.classes

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, note_obj):
        return HttpResponseNotFound("<h1>Brak uprawnień.</h1>")

    if correction_obj.text_style != 'LTX':
        return HttpResponseNotFound("<h1>Poprawki w formacie PDF nie znajeziono.</h1>")

    context = {'latexnote': correction_obj.contents}
    return render_to_pdf(request, 'pdf_note.tex', context=context, filename='notatka')


def correction_download(request, correction_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response

    correction_obj = Correction.objects.filter(id=correction_id)

    if len(correction_obj.all()) != 1:
        return HttpResponseNotFound("<h1>Nieprawidłowy adres http.</h1>")

    correction_obj = correction_obj[0]
    note_obj = correction_obj.note
    classes_obj = note_obj.classes

    if not is_class_creator(user, classes_obj) and not is_note_mine(user, note_obj):
        return HttpResponseNotFound("<h1>Brak uprawnień.</h1>")

    correction_type = {'TXT': 'txt', 'LTX': 'tex', 'MD': 'md'}[correction_obj.text_style]
    response = HttpResponse(correction_obj.contents, content_type={
        'TXT': 'text/plain', 'LTX': 'text/vnd.latex-z', 'MD': 'text/markdown'
    }[correction_obj.text_style])
    response['Content-Disposition'] = f"attachment; filename=poprawka_{correction_id}.{correction_type}"
    return response


def correction_remove(request, correction_id):
    failed_response, user = check_session_user(request)
    if failed_response is not None:
        return failed_response
    
    correction_obj = Correction.objects.filter(author=user, id=correction_id)
    print(correction_obj)
    if len(correction_obj.all()) == 0:
        return HttpResponseNotFound("<h1>Nie znaleziono poprawki.</h1>")
    
    correction_obj[0].delete()
    return redirect('notes')

# Create your views here.
