# -*- coding: utf-8 -*-
import turing
from math import ceil
from flask import Flask, jsonify, request, render_template

application = Flask(__name__)


@application.route('/books')
def books():
    version = '0.1.2'
    return render_template('books.html', version=version)


@application.route('/api/books')
def api_books():
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'date')
    q = request.args.get('q')
    if q:
        books, total = turing.search(q, page - 1, 20, sort)
    else:
        books, total = turing.get_books(page - 1, 20, sort)

    results = {
        'total': total,
        'end': ceil(total / 20),
        'results': books
    }
    return jsonify(results)


if __name__ == '__main__':
    application.run(debug=True)
