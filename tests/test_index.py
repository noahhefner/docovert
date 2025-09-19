def test_index_page(client):
    """
    Verify that the index page ("/") can be requested successfully.

    This test uses the Flask test client to send a GET request to the root
    endpoint and asserts that the response returns HTTP 200 OK, ensuring
    the route is registered and the page renders without errors.
    """

    response = client.get("/")
    assert response.status_code == 200
