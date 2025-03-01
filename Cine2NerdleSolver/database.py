# database.py
import requests
import joblib
import csv
from Cine2NerdleSolver.models import Movie, Person
from Cine2NerdleSolver.config import API_KEY
from collections import defaultdict


class database:
    def __init__(self):
        self.movies = []

    def buildDB(self, count: int):
        '''
        Step 1: Initialize count movies
        '''
        moviesList = []
        page = 1
        while len(moviesList) < count:
            topRatedUrl = (
                f"https://api.themoviedb.org/3/movie/top_rated?"
                f"api_key={API_KEY}&language=en-US&page={page}"
            )
            response = requests.get(topRatedUrl)
            if response.status_code != 200:
                print(f"Request failed with status code {response.status_code}")
                break
            data = response.json()
            results = data.get("results", [])
            if not results:
                break #no more movies(which shouldn't happen since we never look past the first 5000)
            for result in results:
                if len(moviesList) >= count:
                    break
                movie_id = result.get("id")
                details_url = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}?"
                    f"api_key={API_KEY}&language=en-US"
                )
                detailsResponse = requests.get(details_url)
                if detailsResponse.status_code != 200:
                    print(f"Request failed with status code {detailsResponse.status_code}")
                    break
                details = detailsResponse.json()
                title = details.get("title")
                release_date = details.get("release_date")
                # Extract Genres
                genres = [genre.get("name") for genre in details.get("genres")]
                # Extract actors:
                creditsURL = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}/credits?"
                    f"api_key={API_KEY}"
                )
                creditsResponse = requests.get(creditsURL)
                if creditsResponse.status_code != 200:
                    print(f"Request failed with status code {creditsResponse.status_code}")
                    break
                credits = creditsResponse.json()
                people = set()
                cast = credits.get("cast", [])
                crew = credits.get("crew", [])
                # Take up to 10 cast members that have a valid id
                people.update([Person(name=m.get("name"), id=m.get("id"))
                               for m in cast[:10] if m.get("id") is not None])
                # Take up to 5 crew members that have a valid id
                people.update([Person(name=m.get("name"), id=m.get("id"))
                               for m in crew[:5] if m.get("id") is not None])

                movie = Movie(
                    name=title,
                    release_date=release_date,
                    genres=genres,
                    people=people,
                    movies={}
                )
                moviesList.append(movie)
            print("Processed Page: ", page)
            page += 1
        self.movies = moviesList

        # O(n^2) connection. Since the database has < 150k movies and I only compute this once, the inefficiency is fine
        for i, movie_i in enumerate(self.movies):
            for j, movie_j in enumerate(self.movies):
                if i == j:
                    continue
                for personI in movie_i.people:
                    for personJ in movie_j.people:
                        if personI.name == personJ.name and personI.id == personJ.id:
                            for genre in movie_j.genres:
                                movie_i.movies.setdefault(genre, set()).add(j)

        '''
        Step 3: Joblib!!!
        '''
        joblib.dump(self, "databases.joblib")
        print(f"Database built with {len(moviesList)} movies")


    def loadData(self, file_path: str):
        try:
            return joblib.load(file_path)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            return None

    def modifyDB(self, movieStr: str):
        # Manually add whatever buildDB missed out on
        movieURL = (
            f"https://api.themoviedb.org/3/search/movie?query={movieStr}&api_key={API_KEY}"
        )

        response = requests.get(movieURL)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No results found")
            return

        for result in results:
            movie_id = result.get("id")
            details_url = (
                f"https://api.themoviedb.org/3/movie/{movie_id}?"
                f"api_key={API_KEY}&language=en-US"
            )
            detailsResponse = requests.get(details_url)
            if detailsResponse.status_code != 200:
                print(f"Request failed with status code {detailsResponse.status_code}")
                break
            details = detailsResponse.json()
            title = details.get("title")
            release_date = details.get("release_date")
            # Extract Genres
            genres = [genre.get("name") for genre in details.get("genres")]
            # Extract actors:
            creditsURL = (
                f"https://api.themoviedb.org/3/movie/{movie_id}/credits?"
                f"api_key={API_KEY}"
            )
            creditsResponse = requests.get(creditsURL)
            if creditsResponse.status_code != 200:
                print(f"Request failed with status code {creditsResponse.status_code}")
                break
            credits = creditsResponse.json()
            people = set()
            cast = credits.get("cast", [])
            crew = credits.get("crew", [])
            # Take up to 10 cast members that have a valid id
            people.update([Person(name=m.get("name"), id=m.get("id"))
                           for m in cast[:10] if m.get("id") is not None])
            # Take up to 5 crew members that have a valid id
            people.update([Person(name=m.get("name"), id=m.get("id"))
                           for m in crew[:5] if m.get("id") is not None])

            movie = Movie(
                name=title,
                release_date=release_date,
                genres=genres,
                people=people,
                movies={}
            )
            self.movies.append(movie)
            print(movie)

