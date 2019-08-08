import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { UserService } from '../../providers/util/user.service';
import { ToastService } from '../../providers/util/toast.service';

@IonicPage()
@Component({
  selector: 'app-invite',
  templateUrl: './invite.html'
})
export class InvitePage {

  private email: string;

  constructor(private userService: UserService, private toastService: ToastService) { }

  clickInvite() {
    const sessionToken = this.userService.getSessionToken();
    this.userService.post({
      email: this.email,
      session_token: sessionToken
    }, 'invite').then(response => {
      console.log(response);
      if (response['code'] === 1) {
        this.toastService.create('Your invite has been sent!');
      } else {
        this.toastService.create('Your invite has failed to send!');
      }
    });
    this.email = '';
  }

}
