from flask import Flask, render_template_string, request
import datetime

app = Flask(__name__)


@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Калькулятор сауны</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- PWA -->
    <link rel="manifest" href="/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#007AFF">

    <!-- Стиль -->
    <style>
        body {
            font-family: 'Georgia', serif;
            background-color: #f9f7f3;
            color: #2d2a24;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .calculator {
            background: white;
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }

        h1 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #5a4c3b;
        }

        input[type="text"] {
            font-size: 1.2em;
            padding: 10px;
            width: 60px;
            text-align: center;
            border: 1px solid #ccc;
            border-radius: 6px;
            margin: 5px;
        }

        button {
            margin-top: 20px;
            padding: 12px 20px;
            font-size: 1em;
            background-color: #007AFF;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
        }

        button:hover {
            background-color: #005EDB;
        }

        .result {
            margin-top: 20px;
            font-size: 1.3em;
            color: #007AFF;
            font-weight: bold;
        }
    </style>

    <!-- Service Worker -->
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('/static/service-worker.js')
            .then(() => console.log('Service Worker зарегистрирован'))
            .catch(err => console.log('Ошибка регистрации SW:', err));
        });
      }
    </script>
</head>
<body>
    <div class="calculator">
        <h1>Калькулятор стоимости сауны</h1>

        <form method="post">
            <label>Время начала:</label><br>
            <input type="text" name="start_hour" placeholder="16"><br><br>

            <label>Длительность (часов):</label><br>
            <input type="text" name="duration_hour" placeholder="5"><br><br>

            <label>Количество людей:</label><br>
            <input type="text" name="people" placeholder="5"><br><br>

            <label><input type="radio" name="day" value="weekday" checked> Будний день</label><br>
            <label><input type="radio" name="day" value="weekend"> Выходной</label><br><br>

            <button type="submit">Рассчитать</button>
        </form>
    </div>
</body>
</html>
''')


@app.route('/', methods=['POST'])
def calculate():
    try:
        start_hour = int(request.form['start_hour'])
        duration_hours = int(request.form['duration_hour'])
        people = int(request.form['people'])
        day_type = request.form['day']

        tariff_day = 800 if day_type == 'weekday' else 1200
        tariff_night = 1400 if day_type == 'weekday' else 1800

        total_cost = 0.0
        hour_costs = []

        for h in range(duration_hours):
            hour = (start_hour + h) % 24
            is_night = hour >= 17 or hour < 9
            rate = tariff_night if is_night else tariff_day
            cost = rate
            hour_costs.append(cost)
            total_cost += cost

        # Акция 4+1 бесплатно (берём самые дешёвые часы)
        free_hours = len(hour_costs) // 4
        for _ in range(free_hours):
            cheapest = min(hour_costs)
            total_cost -= cheapest
            hour_costs.remove(cheapest)

        # За каждого человека сверх 5
        extra_people = max(0, people - 5)
        total_cost += extra_people * 100 * (duration_hours - free_hours)

        # Генерируем детализацию
        details = []
        for i, cost in enumerate(hour_costs):
            details.append(
                f"{i + 1} ч. {'вечер' if (start_hour + i) % 24 >= 17 or (start_hour + i) % 24 < 9 else 'утро'} → {cost:.0f} ₽")

        return render_template_string('''
<!DOCTYPE html>
<html lang="ru">
<head>
    <title>Результат</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Georgia', serif;
            background-color: #f9f7f3;
            color: #2d2a24;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .calculator {
            background: white;
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }

        h1 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #5a4c3b;
        }

        .result {
            margin-top: 20px;
            font-size: 1.3em;
            color: #007AFF;
            font-weight: bold;
        }

        ul {
            list-style: none;
            padding-left: 0;
            text-align: left;
            margin-top: 10px;
        }

        li {
            margin: 4px 0;
        }
    </style>

    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('/static/service-worker.js');
        });
      }
    </script>
</head>
<body>
<div class="calculator">
    <h1>Калькулятор стоимости сауны</h1>
    <p class="result">Итого: {{ result }} ₽</p>
    <ul>
        {% for line in details %}
            <li>{{ line }}</li>
        {% endfor %}
    </ul>
</div>
</body>
</html>
''', result=f"{total_cost:.2f}", details=details)

    except Exception:
        return "Ошибка ввода данных"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)