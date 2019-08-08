import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { UserService } from '../../providers/util/user.service';
import { ToastService } from '../../providers/util/toast.service';

/**
 * Generated class for the CreateAccountPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-create-account',
  templateUrl: 'create-account.html',
})
export class CreateAccountPage {

  private state = 0;
  private username: string;
  private password: string;
  private confirmation: string;
  private inviteToken: string;
  private houseName: string;
  private houseDescription: string;

  constructor(public navCtrl: NavController, public navParams: NavParams, public userService: UserService, public toastService: ToastService) {
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad CreateAccountPage');
  }

  clickSubmit(amt: number) {
    this.state += amt;
    if (this.state === 2) {
      // Submit and add to existing house
      this.userService.post({
        'username': this.username,
        'password': this.password,
        'invite_token': this.inviteToken
      }, 'register').then(response => {
        if (response['code'] === 1) {
          this.toastService.create('You have been registered!');
          this.navCtrl.setRoot('HomePage');
        } else {
          this.state += 4;
        }

      });
    } else if (this.state === 5) {
      // Submit and create new house
      this.userService.post({
        'username': this.username,
        'password': this.password,
        'house_name': this.houseName,
        'house_description': this.houseDescription
      }, 'register').then(response => {
        if (response['code'] === 1) {
          this.toastService.create('You have been registered!');
          this.navCtrl.setRoot('HomePage');
        } else {
          this.state += 4;
        }
      });
    }
  }

}
