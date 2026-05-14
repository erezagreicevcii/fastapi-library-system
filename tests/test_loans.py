from datetime import date, timedelta


def test_borrow_and_return_book(client, auth_headers, sample_data):
    response = client.post(
        "/api/v1/loans",
        headers=auth_headers,
        json={
            "member_id": sample_data["member"].id,
            "book_id": sample_data["book"].id,
            "due_date": str(date.today() + timedelta(days=14)),
        },
    )

    assert response.status_code == 201
    loan = response.json()
    assert loan["member_id"] == sample_data["member"].id
    assert loan["book_id"] == sample_data["book"].id
    assert loan["return_date"] is None

    return_response = client.post(
        f"/api/v1/loans/{loan['id']}/return",
        headers=auth_headers,
    )

    assert return_response.status_code == 200
    assert return_response.json()["return_date"] == str(date.today())


def test_cannot_borrow_when_no_copies_available(client, auth_headers, sample_data):
    payload = {
        "member_id": sample_data["member"].id,
        "book_id": sample_data["book"].id,
        "due_date": str(date.today() + timedelta(days=14)),
    }

    first_response = client.post("/api/v1/loans", headers=auth_headers, json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/api/v1/loans", headers=auth_headers, json=payload)
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "No copies available"


def test_inactive_member_cannot_borrow(client, auth_headers, sample_data):
    response = client.post(
        "/api/v1/loans",
        headers=auth_headers,
        json={
            "member_id": sample_data["inactive_member"].id,
            "book_id": sample_data["book"].id,
            "due_date": str(date.today() + timedelta(days=14)),
        },
    )

    assert response.status_code == 400


def test_cannot_return_already_returned_loan(client, auth_headers, sample_data):
    create_response = client.post(
        "/api/v1/loans",
        headers=auth_headers,
        json={
            "member_id": sample_data["member"].id,
            "book_id": sample_data["book"].id,
            "due_date": str(date.today() + timedelta(days=14)),
        },
    )

    loan_id = create_response.json()["id"]

    first_return = client.post(f"/api/v1/loans/{loan_id}/return", headers=auth_headers)
    assert first_return.status_code == 200

    second_return = client.post(f"/api/v1/loans/{loan_id}/return", headers=auth_headers)
    assert second_return.status_code == 409
