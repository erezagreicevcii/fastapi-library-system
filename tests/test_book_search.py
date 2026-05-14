from datetime import date, timedelta


def test_book_search_filter_composition(client, auth_headers, sample_data):
    response = client.get(
        "/api/v1/books/search",
        params={
            "q": "Clean",
            "category_id": sample_data["category"].id,
            "author_id": sample_data["author"].id,
            "published_after": 2000,
            "published_before": 2010,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] == 1
    assert data["total_pages"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Clean Code"


def test_book_search_pagination_shape(client, sample_data):
    response = client.get(
        "/api/v1/books/search",
        params={
            "page": 1,
            "page_size": 1,
            "sort_by": "title",
            "sort_order": "asc",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {"items", "page", "page_size", "total", "total_pages"}
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["total"] == 2
    assert data["total_pages"] == 2
    assert len(data["items"]) == 1


def test_book_search_sort_order(client, sample_data):
    response = client.get(
        "/api/v1/books/search",
        params={
            "sort_by": "published_year",
            "sort_order": "desc",
        },
    )

    assert response.status_code == 200
    items = response.json()["items"]

    assert items[0]["title"] == "Refactoring"
    assert items[1]["title"] == "Clean Code"


def test_book_search_available_only(client, auth_headers, sample_data):
    borrow_response = client.post(
        "/api/v1/loans",
        headers=auth_headers,
        json={
            "member_id": sample_data["member"].id,
            "book_id": sample_data["book"].id,
            "due_date": str(date.today() + timedelta(days=14)),
        },
    )
    assert borrow_response.status_code == 201

    response = client.get(
        "/api/v1/books/search",
        params={"available_only": True},
    )

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]

    assert "Clean Code" not in titles
    assert "Refactoring" in titles
