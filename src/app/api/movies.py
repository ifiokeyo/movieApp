import os

import logging
from typing import List
from json import loads, dumps

import requests
from requests.exceptions import ConnectionError

import redis

from src.app.models.models import Movie, Person


redis_db = redis.from_url(os.environ.get('REDIS_URL'))


def _get_people():
    """
    Makes a request to the external API for people.
    :return: A modified array of person object.
    """
    try:
        response = requests.get("https://ghibliapi.herokuapp.com/people")
        count = 0
        if response.status_code == 200:
            people = loads(response.text)

            for person in people:
                if len(person['films']) != 0:
                    count += 1
                person['films'] = [film.split('https://ghibliapi.herokuapp.com/films/')[1] for film in person['films']]
            return people
        return None, count
    except ConnectionError as e:
        logging.error(e)
        return None


def _update_cache_and_db():
    """
    Updates the database and Cache db with recent movie and people data.
    :return: an array of movies with their associated cast where present.
    """
    api_res = requests.get("https://ghibliapi.herokuapp.com/films")

    if api_res.status_code != 200:
        status = api_res.status_code
        return loads(api_res.text), status

    films = loads(api_res.text)

    for film in films:
        movie = Movie.query.get(film['id'])
        if movie is None:
            new_movie = Movie(
                id=film['id'], title=film['title'], description=film['description'],
                director=film['director'], producer=film['producer'],
                releaseDate=film['release_date'], rating=film['rt_score']
            )
            new_movie.save()

    people = _get_people()

    if people:
        for person in people:
            record = Person.query.get(person['id'])
            if record is None:
                new_person = Person(
                    id=person['id'], name=person['name'],
                    age=person['age'], gender=person['gender'],
                    eyeColor=person['eye_color'], hairColor=person['hair_color']
                )

                updated_person = _add_movie_to_user_movies(new_person, person['films'])

                updated_person.save()
            else:
                updated_person = _add_movie_to_user_movies(record, person['films'])
                updated_person.update()

    all_movies = Movie.query.all()

    results = []

    for mov in all_movies:
        mov_cast = [actor.serialize() for actor in mov.people]
        serialized_mov = mov.serialize()
        serialized_mov['people'] = mov_cast
        results.append(serialized_mov)

    redis_db.set('movies', dumps(results))

    return results


def _add_movie_to_user_movies(user, movie_ids: List):
    """
    Updates the movie-cast pivot table for a particular person object
    :param user:
    :param movie_ids:
    :return: a person object
    """
    movies = []
    for movie_id in movie_ids:
        record = Movie.query.get(movie_id)
        if record is not None:
            movies.append(record)
    user.movies = movies
    return user


def _get_movies_from_db():
    """
    Retrieve all movies from the database
    :return: an array of movies
    """
    db_movies = Movie.query.all()

    response_tray = []

    for mov in db_movies:
        mov_cast = [actor.serialize() for actor in mov.people]
        serialized_mov = mov.serialize()
        serialized_mov['people'] = mov_cast
        response_tray.append(serialized_mov)

    return response_tray


def get_movies():
    """
    Get all movies with their associated cast. Retrieves from cache if present,
    Otherwise, pulls from the external API and updates the db and cache after
    necessary processing and transformation.
    :return: an array of movies
    """
    try:
        cache_res = redis_db.get('movies')
        if cache_res is not None:
            results = loads(cache_res)
        else:
            results = _update_cache_and_db()

        return results
    except Exception as error:
        logging.error(error)
        try:
            response = _get_movies_from_db()

            return response
        except Exception as e:
            logging.error(e)
            return "Server error"

