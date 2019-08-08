import { Component, OnInit } from '@angular/core';
import { IonicPage, NavController } from 'ionic-angular';

import { UserService } from '../../providers/util/user.service';

@IonicPage()
@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage implements OnInit {

  scores = {};
  
// FOR THE CHORE CARD 
  items = [
    {
      chore: 'Dishes',
      nickName: 'Bobby',
      dueDate: 'Mon',
      description: 'Description and stuff goes here',
      isComplete: 'incomplete',
      assignees: 'Jane, Bob, Joe',
    }
  ]

  item2s = [
    {
      chore: 'Dishes',
      nickName: 'Bobby',
      dueDate: 'Mon',
      score: '50',
      description: 'Description and stuff goes here',
      isComplete: 'incomplete',
      assignees: 'Jane, Bob, Joe',
    }
  ]


  constructor(public userService: UserService) {}

  ngOnInit() {
    this.userService.getScores().then(response => {
      this.scores = response;
    });
  }
  
//FOR SCORE CARD DIPLAYED IN HOUSE

}


