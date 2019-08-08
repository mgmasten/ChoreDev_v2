import { Component, OnInit } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { UserService } from '../../providers/util/user.service';
import { ToastService } from '../../providers/util/toast.service';

/**
 * Generated class for the CreateChorePage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-create-chore',
  templateUrl: 'create-chore.html',
})
export class CreateChorePage implements OnInit {
  name: string;
  description: string;
  difficulty: string;
  occursOn;
  assignments;
  users = [];

  constructor(public navCtrl: NavController, 
    public navParams: NavParams, 
    public userService: UserService,
    public toastService: ToastService) {
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad CreateChorePage');
  }

  ngOnInit() {
    this.load();
  }

  load() {
    this.userService.getUsers().then(response => {
      this.users = response;
    }).catch(error => {
      this.toastService.create('Oops! Please reload this page.');
    });
  }

  clickCreate() {
    this.userService.post({
      'session_token': this.userService.getSessionToken(),
      name: this.name,
      description: this.description,
      'eligible_assignees': this.assignments,
      difficulty: this.difficulty,
      occurs_on: this.occursOn
    }, 'chore/add').then(response => {
      if (response['code'] === 1) {
        this.toastService.create('Success!');
        this.name = '';
        this.description = '';
        this.assignments = [];
        this.difficulty = '';
        this.occursOn = [];
      } else {
        this.toastService.create('Error :( Try again!');
      }

    }).catch(error => {
      this.toastService.create('Error :( Try again!');
    });
    
  }

}
