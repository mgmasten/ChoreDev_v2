import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

@IonicPage()
@Component({
  selector: 'page-settings',
  templateUrl: 'settings.html',
})
export class SettingsPage {

  items = [
    {
      name: 'Profile',
      username: 'temp_username',
      email: 'temp_email',
    },
  ];
  houses = [
    {
      name: 'House',
      houseName: 'tempHouseName',
      description: 'about the house',
      houseMates: 'Jane, Bob',
      chores:'Dishes, Trash, Floors'

    },
  ];

  constructor(public navCtrl: NavController, public navParams: NavParams) {
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad SettingsPage');
  }


}
