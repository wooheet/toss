import * as React from 'react';
import { userStore, postStore } from './store';

function useStore() {
  return { userStore, postStore };
}

export default useStore;