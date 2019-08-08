import { Component, ElementRef, Input, Renderer, ViewChild, OnInit } from '@angular/core';

@Component({
  selector: 'score',
  templateUrl: 'score.html'
})
export class ScoreComponent implements OnInit {

  @Input() data;
  myDate: String = new Date().toISOString();
  constructor(public renderer: Renderer) { }

  ngOnInit() {

  }

}
