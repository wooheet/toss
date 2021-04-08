import React, { useCallback } from 'react';
import { observer, useLocalObservable } from 'mobx-react';
import useStore from '../Stores/Use';
import styled, { ThemeProvider } from "styled-components";
import { HashRouter as Router } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import GlobalStyles from "../Styles/GlobalStyles";
import Theme from "../Styles/Theme";
import Routes from "./Router";
import Footer from "./Footer";
import Header from "./Header";

// import { gql } from "apollo-boost";
// import { useQuery } from "react-apollo-hooks";

// const QUERY = gql`
//   {
//     isLoggedIn @client
//   }
// `;

const Wrapper = styled.div`
  margin: 0 auto;
  max-width: ${props => props.theme.maxWidth};
  width: 100%;
`;

export default () => {
  // const {
  //   data: { isLoggedIn }
  // } = useQuery(QUERY);

  const { userStore, postStore } = useStore();

  return (
    <ThemeProvider theme={Theme}>
      <>
        <GlobalStyles />
        <Router>
          <>
            <Header />
            <Wrapper>
              <Routes isLoggedIn />
              <Footer />
            </Wrapper>
          </>
        </Router>
        <ToastContainer position={toast.POSITION.BOTTOM_LEFT} />
      </>
    </ThemeProvider>
  );
};


// import React, { useCallback } from 'react';
// import { observer, useLocalObservable } from 'mobx-react';
//
// import useStore from './useStore';
//
// const App = () => {
//   const { userStore, postStore } = useStore();
//
//   const state = useLocalObservable(() => ({
//     name: '',
//     password: '',
//     onChangeName(e) {
//       this.name = e.target.value;
//     },
//     onChangePassword(e) {
//       this.password = e.target.value;
//     }
//   }));
//
//   const onClick = useCallback(() => {
//     userStore.logIn({
//       nickname: 'zerocho',
//       password: '비밀번호',
//     });
//   }, []);
//
//   const onLogout = useCallback(() => {
//     userStore.logOut();
//   }, []);
//
//   return (
//     <div>
//       {userStore.isLoggingIn
//         ? <div>로그인 중</div>
//         : userStore.data
//           ? <div>{userStore.data.nickname}</div>
//           : '로그인 해주세요.'}
//       {!userStore.data
//         ? <button onClick={onClick}>로그인</button>
//         : <button onClick={onLogout}>로그아웃</button>}
//       <div>{postStore.postLength}</div>
//       <input value={state.name} onChange={state.onChangeName} />
//       <input value={state.password} type="password" onChange={state.onChangePassword}  />
//     </div>
//   );
// };
//
// export default observer(App);