"""A module that will support adding issues to various
pyOpenSci project boards.


# This is a great tool to test queries - https://docs.github.com/en/graphql/overview/explorer
https://docs.github.com/en/graphql/guides/introduction-to-graphql#discovering-the-graphql-api

The query below can be used in the explorer tester above to see all endpoints
query {
  __type(name: "Issue") {
    name
    kind
    description
    fields {
      name
    }
  }
}

query issues

query {
  repository(owner:"pyopensci", name:"software-review") {
    issues(last:40, states:OPEN) {
      edges {
        node {
          title
          url
          labels(first:5) {
            edges {
              node {
                name
              }
            }
          }
        }
      }
    }
  }
}

Get approved issues

{
  repository(owner: "pyopensci", name: "software-review") {
    issues(first: 20, states: OPEN, filterBy: {labels: "6/pyOS-approved 🚀🚀🚀"}) {
      edges {
        node {
          title
          url
          labels(first: 5) {
            edges {
              node {
                name
              }
            }
          }
        }
      }
    }
  }
}

https://github.com/orgs/community/discussions/68769#discussioncomment-7164824


TODOs
* the code below is working in that is will move an issue on the project board.
1. The next step would be to get a list of all open review issues (using pyos meta)
2. Create a dict with the issue number and it's labels in a list
3. Create another dict that has the issue id and the status it should be on the board

"""

# import os
import requests

# GitHub GraphQL endpoint
graphql_endpoint = "https://api.github.com/graphql"

# Your personal access token
# access_token = os.getenv("ACCESS_TOKEN")
# Scoped to repo and project access, classic token
ACCESS_TOKEN = ""
PROJECT_NUM = 10
ORGANIZATION = "pyopensci"


def get_ql_query_response(access_token, query):
    """Retrieves a response from a GraphQL endpoint.

    Parameters
    ----------
    query : str
        The GraphQL query string.
    access_token : str
        The access token used for authorization.

    Returns
    -------
    dict
        The JSON response from the GraphQL endpoint.
    """
    graphql_endpoint = "https://api.github.com/graphql"
    # Headers with authorization
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Make GraphQL query to fetch project board ID
    print("Request URL:", graphql_endpoint)
    print("Request Headers:", headers)
    print("Request Body:", {"query": query})

    # Make GraphQL query to fetch project board ID
    response = requests.post(
        graphql_endpoint, json={"query": query}, headers=headers
    )
    print(response.json())

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Query failed to run with a status code {response.status_code}. Response: {response.text}"
        )
    return response.json()


def get_project_id(project_number, access_token):
    """GraphQL query to fetch project board ID
    this is working!

    """
    query = """
    query {
      organization(login: "pyopensci") {
        projectV2(number: %d) {
          id
        }
      }
    }
    """ % (
        project_number,
    )

    data = get_ql_query_response(query=query, access_token=access_token)

    # Extract project board ID
    try:
        project_id = data["data"]["organization"]["projectV2"]["id"]
        return project_id
    except KeyError:
        print("Project board not found.")
        return None


def get_project_field(project_id, access_token):
    """Next: get field (status) within our board?

    https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects#finding-the-node-id-of-a-field
    """

    query = (
        """
    query {
        node(id: "%s") {
            ... on ProjectV2 {
                fields(first: 20) {
                    nodes {
                        ... on ProjectV2Field {
                            id
                            name
                        }
                        ... on ProjectV2IterationField {
                            id
                            name
                            configuration {
                                iterations {
                                    startDate
                                    id
                                }
                            }
                        }
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                            options {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """
        % project_id
    )

    return get_ql_query_response(access_token=access_token, query=query)


def get_project_items(project_id, access_token):
    """
    Retrieve information about a project using GraphQL query.

    Parameters
    ----------
    project_id : str
        The ID of the project.
    access_token : str

    Returns
    -------
    dict
        The response containing project information.
    """
    query = (
        """
    query {
        node(id: "%s") {
            ... on ProjectV2 {
                items(first: 20) {
                    nodes {
                        id
                        fieldValues(first: 8) {
                            nodes {
                                ... on ProjectV2ItemFieldTextValue {
                                    text
                                    field {
                                        ... on ProjectV2FieldCommon {
                                            name
                                        }
                                    }
                                }
                                ... on ProjectV2ItemFieldDateValue {
                                    date
                                    field {
                                        ... on ProjectV2FieldCommon {
                                            name
                                        }
                                    }
                                }
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    name
                                    field {
                                        ... on ProjectV2FieldCommon {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                        content{
                            ...on Issue {
                                title
                                labels(first: 10) {  # fetch labels
                                nodes {
                                    name
                                }
                            }
                                assignees(first: 10) {
                                    nodes{
                                        login
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
        % project_id
    )

    return get_ql_query_response(access_token=access_token, query=query)


def update_issue_status(
    access_token, project_id, item_id, field_id, option_id
):
    """
    Update a ProjectV2 item field value using a GraphQL query.

    This updates the status of a review issue on our project board
    based upon the current label(s) on the issue.

    Parameters
    ----------
    access_token : str
        The GitHub access token for authorization.
    project_id : str
        The ID of the Github project board.
    item_id : str
        The ID of the item (an issue) within the project that we want to
        update the status of.
    field_id : str
        The ID of the existing status field (to be updated). For pyOS peer
        review this is the status field (of the review).
    option_id : str
        The ID of the board "status" option to set as the new value/status for
        the issue on the board.
        Example status values include under-review, pyos-accepted,
        out-of-scope, etc

    Returns
    -------
    dict
        The response containing the updated project item information.
    """
    # GraphQL mutation string
    mutation_query = """
    mutation {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: "%s"
          itemId: "%s"
          fieldId: "%s"
          value: {
            singleSelectOptionId: "%s"
          }
        }
      ) {
        projectV2Item {
          id
        }
      }
    }
    """ % (
        project_id,
        item_id,
        field_id,
        option_id,
    )

    return get_ql_query_response(
        access_token=access_token, query=mutation_query
    )


"""
"name": "Status",
            "options": [
              {
                "id": "0d229fa2",
                "name": "pre-review-checks"
              },
              {
                "id": "f75ad846",
                "name": "under-review"
              },
              {
                "id": "109fa81a",
                "name": "pyos-accepted"
              },
              {
                "id": "47fc9ee4",
                "name": "pre-submission"
              },
              {
                "id": "98236657",
                "name": "Joss accepted"
              },
              {
                "id": "b455ee2a",
                "name": "out-of-scope"
              },
              {
                "id": "ef5d71a5",
                "name": "on-hold-or-maintainer-unresponsive"
              },
              {
                "id": "164e36bb",
                "name": "under-joss-review"
              }
"""


# This works
project_id = get_project_id(PROJECT_NUM, ACCESS_TOKEN)
# Get project field id
project_field = get_project_field(project_id, ACCESS_TOKEN)
status_field_id = project_field["data"]["node"]["fields"]["nodes"][2]["id"]

# Get project types (these represent the columns in the project board)
# Here the id is the value of the field and the node is the text name
all_fields = project_field["data"]["node"]["fields"]["nodes"][2]["options"]
status_option_id = "f75ad846"  # under review

# Get a list of all issues currently on the board
# I can use this to get the issue id and status
project_items = get_project_items(project_id, ACCESS_TOKEN)
# Each node from the query below represents an issue id that is in the board.
item_id = project_items["data"]["node"]["items"]["nodes"][0]["id"]


# Project id is the project board id
# this updates an issue on the board.
"""
The query below moves the first issue node 0 which is junos test package review
from it's current status to "under review"
We'd actually want to look at the issue, get it's current label, and then
move it accordingly.

"""
# TODO: above i modified the query to return labels for each issue too
# I now have enough information to update the project board based upon the
# labels in the current issue!

# Create column mapping that i want to use
column_name_mapping = {
    "1/editor-assigned": "under-review",  # Example label and corresponding column name
    "Label2": "In Progress",
    "Label3": "Done",
}

# loop through each node - compare the status to the column mapping associated
# with it's labels.

# If there is a mismatch in labels, then identify what status it should have
# then move it to that status column.


update_issue_status(
    ACCESS_TOKEN, project_id, item_id, status_field_id, status_option_id
)


# this will update a single field for a single item
# https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects#updating-a-single-select-field


# def get_project_board_column_id(project_name, column_name, access_token):
#     # GraphQL query to fetch project board column ID
#     my_org = "octo-org"
#     my_num = project_number
#     query = (
#         """
#     query {
#       organization(login: "pyopensci") {
#         projectV2(number: $number) {
#           id
#           columns(first: 100) {
#             nodes {
#               id
#               name
#             }
#           }
#         }
#       }
#     }
#     """
#         % project_number
#     )

#     # Headers with authorization
#     headers = {"Authorization": f"Bearer {access_token}"}

#     # Make GraphQL query to fetch project board column ID
#     response = requests.post(
#         graphql_endpoint, json={"query": query}, headers=headers
#     )
#     data = response.json()

#     # Extract column ID
#     columns = data["data"]["organization"]["project"]["columns"]["nodes"]
#     for column in columns:
#         if column["name"] == column_name:
#             return column["id"]
#     return None


# def move_card_to_column(card_id, column_id):
#     # GraphQL mutation to update card's status
#     mutation = """
#     mutation {
#       moveProjectCard(input: {cardId: "%s", columnId: "%s"}) {
#         clientMutationId
#       }
#     }
#     """ % (
#         card_id,
#         column_id,
#     )

#     # Make GraphQL mutation to update card's status
#     response = requests.post(
#         graphql_endpoint, json={"query": mutation}, headers=headers
#     )

#     # Check response
#     if response.status_code == 200:
#         print("Card status updated successfully!")
#     else:
#         print("Failed to update card status.")
#         print(response.text)


# def get_issue_labels(owner, repo, issue_number):
#     api_endpoint = (
#         "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
#     )

#     # Construct the API URL for fetching issue details
#     url = api_endpoint.format(
#         owner=owner, repo=repo, issue_number=issue_number
#     )
#     # Headers with authorization
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Accept": "application/vnd.github.v3+json",
#     }
#     # Make request to fetch issue details
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         data = response.json()
#         return [label["name"] for label in data["labels"]]
#     else:
#         print(f"Failed to fetch issue details: {response.text}")
#         return []


def main():
    # Get issue details from environment variables set by GitHub Actions
    issue_number = 19  # os.getenv("ISSUE_NUMBER")
    project_name = PROJECT_BOARD
    column_name_mapping = {
        "1/editor-assigned": "under-review",  # Example label and corresponding column name
        "Label2": "In Progress",
        "Label3": "Done",
    }

    labels = get_issue_labels("pyopensci", "test-pyos-review", issue_number)

    # Get the label of the updated issue
    # labels = os.getenv("LABELS").split(",")
    updated_label = None
    for label in labels:
        if label in column_name_mapping:
            status = column_name_mapping[label]
            break

    if updated_label is None:
        print("No relevant label found.")
        return

    # Determine the corresponding column name from the label
    # target_column_name = column_name_mapping[updated_label]

    # Get the column ID of the target column
    column_id = get_project_board_column_id(PROJECT_BOARD, status)
    if column_id is None:
        print("Target column not found.")
        return

    # Move the card to the target column
    move_card_to_column(issue_number, column_id)


if __name__ == "__main__":
    main()
