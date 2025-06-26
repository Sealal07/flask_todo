from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect  # Импортируем inspect для проверки таблиц

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем устаревшую функцию
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)  # Добавляем поле для статуса задачи


# Декоратор, который регистрирует маршрут '/' (главная страница)
# и разрешает методы GET (для отображения страницы) и POST (для отправки формы)
@app.route('/', methods=['GET', 'POST'])
def index():
    # Проверяем, был ли запрос методом POST (отправка формы)
    if request.method == 'POST':
        # Получаем текст задачи из формы (из поля с именем 'text')
        task_text = request.form['text']

        # Создаем новый объект Task (новую запись в БД) с полученным текстом
        new_task = Task(text=task_text)

        # Добавляем новую задачу в сессию базы данных (пока не сохранено)
        db.session.add(new_task)

        # Фиксируем изменения в базе данных (сохраняем задачу)
        db.session.commit()

        # Перенаправляем пользователя обратно на главную страницу
        # чтобы избежать повторной отправки формы при обновлении
        return redirect('/')

    # Если запрос GET (обычная загрузка страницы),
    # получаем ВСЕ задачи из базы данных
    tasks = Task.query.all()

    # Рендерим шаблон index.html, передавая в него список задач
    # Шаблон сможет использовать переменную tasks для отображения
    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)  # Находим задачу
    db.session.delete(task)           # Удаляем
    db.session.commit()              # Сохраняем
    return redirect('/')             # Возвращаемся на главную



@app.route('/toggle/<int:id>')
def toggle(id):
    task = Task.query.get_or_404(id)
    task.is_done = not task.is_done  # Меняем статус на противоположный
    db.session.commit()
    return redirect('/')

# Проверяем, запущен ли скрипт напрямую
if __name__ == '__main__':
    with app.app_context():
        # Создаем инспектор для проверки базы данных
        inspector = inspect(db.engine)

        # Проверяем существование таблицы правильным способом
        if not inspector.has_table('task'):
            db.create_all()
            print("Таблица 'task' создана")
        else:
            print("Таблица 'task' уже существует")

    app.run(debug=True)