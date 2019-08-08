import { Injectable } from '@angular/core';

import { Http, Headers, RequestOptions } from '@angular/http';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';

@Injectable()
export class UserService {

  private sessionToken = '';
  private users = [];
  private scores = {};
  private headers = new Headers({
    Accept: 'application/json',
    'Content-Type': 'application/json'
  });
  private options = new RequestOptions({ headers: this.headers });
  private url = 'http://127.0.0.1:5000/';
  private username = '';

  constructor(private http: Http) {
    // this.http.setDataSerializer('json');
  }

  // https://beta.ionicframework.com/docs/native/http/
  post(data, endpoint) {
    return new Promise((resolve, reject) => {
      this.http.post(this.url + endpoint, data, this.options).toPromise().then(response => {
        resolve(response.json());
      }).catch(error => {
        reject(error);
      });
    });
  }

  getUsers() {
    return this.post({
      'session_token': this.sessionToken
    }, 'house/get_users').then(response => {
      if (response['code'] === 1) {
        this.users = response['users'];
      }
      return this.users;
    }).catch(error => {
      return error;
    });
  }

  getScores() {
    return this.post({
      'session_token': this.getSessionToken()
    }, 'score/get_weekly_scores').then(response => {
      return response;
    }).catch(error => {
      return error;
    });
  }

  loggedIn() {
    return this.sessionToken !== '';
  }

  getUserProfile() {
       return this.post({
            'session_token': this.sessionToken
       }, 'user/get').then(response => {
              return response;
         }).catch(error => {
              return error;
         });
}

  getHouseProfile() {
       return this.post({
            'session_token': this.sessionToken
     }, 'user/get_house_profile').then(response => {
               return response;
     }).catch(error => {
          return error;
     });
 }

  logout(resetSession = true) {
    return this.post({ session_token: this.sessionToken }, 'logout').then(response => {
      if (resetSession) {
        this.sessionToken = ''
      }
      this.username = '';
      this.scores = {};
      this.users = [];
      return response;
    }).catch(error => {
      console.log(error);
      return error;
    });
  }

  getSessionToken() {
    return this.sessionToken;
  }

  setSessionToken(token: string) {
    this.sessionToken = token;
  }

  setUsername(username: string) {
    this.username = username;
  }

  getUsername() {
    return this.username;
  }

}
