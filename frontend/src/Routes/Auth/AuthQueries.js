import { gql } from "apollo-boost";

export const LOG_IN = gql`
  mutation tokenAuth(
    $username: String!
    $password: String!
   ) {
    tokenAuth(
        username: $username
        password: $password
    ) {
        token
    }
  }
`;

export const CREATE_ACCOUNT = gql`
  mutation createUser(
    $username: String!
    $email: String!
    $firstName: String
    $lastName: String
  ) {
    createUser(
      username: $username
      email: $email
      firstName: $firstName
      lastName: $lastName
      password: $firstName
    ) {
        user{
          id
          username
          email
        }
    }
  }
`;

export const CONFIRM_SECRET = gql`
  mutation confirmSecret($secret: String!, $email: String!) {
    confirmSecret(secret: $secret, email: $email)
  }
`;

export const LOCAL_LOG_IN = gql`
  mutation logUserIn($token: String!) {
    logUserIn(token: $token) @client
  }
`;