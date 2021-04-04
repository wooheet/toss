import ApolloClient from "apollo-boost";
import { defaults, resolvers } from "./LocalState";

export default new ApolloClient({
  uri: "http://127.0.0.1:8000/graphql/",
  clientState: {
    defaults,
    resolvers
  }
});