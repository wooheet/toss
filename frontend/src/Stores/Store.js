import { observable, action } from 'mobx';

export default class Store {
  @observable store = 'hello';

  @action changeStoreValue = value => {
    this.store = value;
  };
  @action changeToWorld = () => {
  	this.store = "World";
  }
}