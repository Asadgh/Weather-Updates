from flask import Flask, render_template, request, jsonify, redirect, make_response, abort
from weather import get_daily_weather, get_hourly_weather, jobber
from my_scripts import hour_handler, wind_type, emailer
import json


app = Flask(__name__)

with open("app_defaults.json", "r") as fileh:
    app_json = json.load(fileh)

APIKEY = app_json['APIKEY']
NESTS = app_json['NESTS']

nests = list(NESTS.keys())
nests.sort()
launcher_dirs = ('north', 'south')


@app.route('/save_settings', methods=['GET'])
def save_settings():
    # Get the settings from the GET request
    settings = {
        'cur_nest': request.args.get('cur_nest'),
        'launcher_dir': request.args.get('launcher')
    }

    if settings['cur_nest'] in nests and settings['launcher_dir'] in launcher_dirs:
        # Create a response to redirect to /dashboard
        response = make_response(redirect('/dashboard'))

        # Set the settings in a cookie
        response.set_cookie('settings', json.dumps(settings))

        return response
    else:
        abort(400)


@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    direction = data.get('direction')

    if direction in launcher_dirs:
        settings = json.loads(request.cookies.get('settings', '{}'))
        settings['launcher_dir'] = direction

        resp = make_response()
        resp.set_cookie('settings', json.dumps(settings))

        return resp
    else:
        abort(400)


@app.route('/')
def index():
    settings = json.loads(request.cookies.get('settings', '{}'))

    if settings == {} or ('nest' not in dict(settings).keys() and 'launcher_dir' not in dict(settings).keys()):
        return render_template('index.html', data={
            'nests': nests,
            'nests_dict': NESTS,
        })
    else:
        return redirect('/dashboard')


@app.route('/home')
def home():
    return render_template('index.html', data={
        'nests': nests,
        'nests_dict': NESTS,
    })


@app.route('/dashboard', methods=['GET'])
def dashboard():
    settings = json.loads(request.cookies.get('settings', '{}'))

    selected_nest = settings['cur_nest']
    launcher_dir = settings['launcher_dir']

    jobber()

    daily_weather_info = get_daily_weather(selected_nest)
    hourly_weather_info = get_hourly_weather(selected_nest)

    wind_deg = daily_weather_info['wind_dir_deg']
    daily_weather_info['wind_dir'] = f"{daily_weather_info['wind_dir']} ({wind_type(wind_deg, launcher_dir)})"

    wind_gust_deg = daily_weather_info['wind_gust_dir_deg']
    daily_weather_info[
        'wind_gust_dir'] = f"{daily_weather_info['wind_gust_dir']} ({wind_type(wind_gust_deg, launcher_dir)})"

    wind_deg_hourly = hourly_weather_info['max_wind_deg']
    hourly_weather_info[
        'max_wind_dir'] = f"{hourly_weather_info['max_wind_dir']} ({wind_type(wind_deg_hourly, launcher_dir)})"

    hourly_weather_info['max_wind_hr'] = hour_handler(
        hourly_weather_info['max_wind_hr'])
    hourly_weather_info['max_wind_gust_hr'] = hour_handler(
        hourly_weather_info['max_wind_gust_hr'])
    hourly_weather_info['max_temp_hr'] = hour_handler(
        hourly_weather_info['max_temp_hr'])

    return render_template('dashboard.html', data={
        'nest': NESTS[selected_nest][0],
        'nests': nests,
        'nests_dict': NESTS,
        'daily': daily_weather_info,
        'hourly': hourly_weather_info,
        'launcher_dir': launcher_dir,
        'launcher_dirs': launcher_dirs,
    })


@app.route('/unique/<nest>')
def unique(nest):
    if nest in nests:
        settings = json.loads(request.cookies.get('settings', '{}'))
        settings['cur_nest'] = nest

        resp = make_response(redirect('/dashboard'))
        resp.set_cookie('settings', json.dumps(settings))

        return resp
    else:
        abort(404)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    return render_template('feedback.html')


@app.route('/feedback_info', methods=['GET', 'POST'])
def feedback_info():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('number')
        message = request.form.get('message')

        emailer({'name': name,
                'email': email,
                'number': number,
                'message': message})

    return redirect('/')  


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400


if __name__ == '__main__':
    app.run(debug=True)
