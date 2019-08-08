import { Component, OnInit } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { UserService } from '../../providers/util/user.service';

/**
 * Generated class for the ScorePage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-score',
  templateUrl: 'score.html',
})
export class ScorePage implements OnInit {

 
  item2s = [
    {
      name: 'Dishes',
      username: 'Bobby',
      dueDate: 'Mon',
      score: '50',
      description: 'Description and stuff goes here',
      isComplete: 'incomplete',
      assignees: 'Jane, Bob, Joe',
    }
  ]

  scores = {};

  constructor(public navCtrl: NavController, public navParams: NavParams, public userService: UserService) {
  }

  ngOnInit() {
    this.userService.getScores().then(response => {
      console.log(response);
      this.scores = response;
    });
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad ScorePage');
  }

}
