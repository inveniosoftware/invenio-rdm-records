def test_search_record_suggested_communities(
    client,
    community,
    community2,
    record_community,
    open_review_community,
    uploader,
    inviter,
    headers,
):
    """Test search of suggested communities for a record."""
    record = record_community.create_record()

    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions",
        headers=headers,
        json={},
    )

    assert response.status_code == 403

    client = uploader.login(client)
    # Return user communities that are eligible to upload to.
    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions",
        headers=headers,
        json={},
    )
    assert response.status_code == 200

    # Check that all communities are suggested
    hits = response.json["hits"]
    assert hits["total"] == 2
    assert hits["hits"][0]["id"] == open_review_community.id

    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions?membership=true",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    hits = response.json["hits"]
    assert hits["total"] == 0

    # add record to a community
    data = {
        "communities": [
            {"id": open_review_community.id},  # test with id
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200
    assert response.json["processed"][0]["community_id"] == open_review_community.id

    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions",
        headers=headers,
        json={},
    )
    assert response.status_code == 200

    # Make sure the community is no longer suggested
    hits = response.json["hits"]
    assert hits["total"] == 1
    assert hits["hits"][0]["id"] != open_review_community.id
