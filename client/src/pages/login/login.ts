import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { UserService } from '../../providers/util/user.service';
import { ToastService } from '../../providers/util/toast.service';

/**
 * Generated class for the LoginPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-login',
  templateUrl: 'login.html',
})
export class LoginPage {

  private username: string;
  private password: string;
  private state = 0;

  constructor(public navCtrl: NavController, public navParams: NavParams, public userService: UserService, public toastService: ToastService) {
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad LoginPage');
  }

  clickLogin() {
    this.state++;
    this.userService.post({
      'username': this.username,
      'password': this.password
    }, 'login').then(response => {
      if (response['code'] === 1) {
        setTimeout(() => {
          this.userService.setSessionToken(response['session_token']);
          this.toastService.create('Logged in!');
          this.navCtrl.setRoot('HomePage');
          this.userService.setUsername(this.username);
        }, 1000);
      } else if (response['code'] === -2 || response['code'] === 0) {
        this.toastService.create('Incorrect user or password!');
        this.password = '';
        this.state--;
      }
    });
  }
}
