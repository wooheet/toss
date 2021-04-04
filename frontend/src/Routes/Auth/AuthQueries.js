import { gql } from "apollo-boost";

export const LOG_IN = gql`    
  mutation createUser(
            $email: String!
            $username: String!
        ) {
        createUser(
            email: $email
            username: $username
        ) {
            email
        }
    }
`;

export const CREATE_ACCOUNT = gql`
  mutation createAccount(
    $username: String!
    $email: String!
    $firstName: String
    $lastName: String
  ) {
    createAccount(
      username: $username
      email: $email
      firstName: $firstName
      lastName: $lastName
    )
  }
`;