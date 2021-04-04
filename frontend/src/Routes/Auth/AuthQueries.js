import { gql } from "apollo-boost";

export const LOG_IN = gql`    
  mutation requestSecret(
            $email: String!
        ) {
        requestSecret(
            email: $email
        ) {
            isSecret       
        }
    }
`;

export const CREATE_ACCOUNT = gql`
  mutation createAccount(
            $email: String!
            $username: String!
            $password: String!
        ) {
        createAccount(input:{
                email: $email
                username: $username
                password: $password
            }
        ) {
            user {
                id,
                email,
                password,
                username,
            }
        }
    }
`;