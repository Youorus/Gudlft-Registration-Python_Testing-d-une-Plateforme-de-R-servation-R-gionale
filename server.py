import json
from flask import Flask, render_template, request, redirect, flash, url_for, session


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        email = request.form['email']
        if not email.strip():  # Vérifie si l'email est vide ou ne contient que des espaces
            raise ValueError("Email cannot be empty. Please try again.")

        club = next(club for club in clubs if club['email'] == email)
        return render_template('welcome.html', club=club, competitions=competitions)

    except StopIteration:
        flash("Email not found. Please try again.")
        return redirect(url_for('index'))
    except KeyError:
        flash("Invalid form submission. Please try again.")
        return redirect(url_for('index'))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}")
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next(c for c in clubs if c['name'] == club)
    foundCompetition = next(c for c in competitions if c['name'] == competition)
    return render_template('booking.html', club=foundClub, competition=foundCompetition)

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    try:
        # Récupérer les données du formulaire
        competition = next(c for c in competitions if c['name'] == request.form['competition'])
        club = next(c for c in clubs if c['name'] == request.form['club'])
        places_required = int(request.form['places'])

        # Vérifier les contraintes
        if places_required <= 0:
            raise ValueError("Invalid number of places. Please enter a positive number.")
        if places_required > 12:
            raise ValueError("You cannot book more than 12 places in a competition.")
        if places_required > int(club['points']):
            raise ValueError("You do not have enough points to make this booking.")
        if places_required > int(competition['numberOfPlaces']):
            raise ValueError("Not enough places available in this competition.")

        # Mettre à jour les données
        club['points'] = int(club['points']) - places_required
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required

        # Confirmation
        flash(f"Great-booking complete! {places_required} places booked.")
        return render_template('welcome.html', club=club, competitions=competitions)

    except (ValueError, StopIteration) as e:
        # Gestion des erreurs
        flash(str(e))
        return redirect(url_for('book', competition=request.form['competition'], club=request.form['club']))


@app.route('/pointsDisplay')
def pointsDisplay():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))