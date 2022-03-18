<template>
  <div>
    <div class="mar-large full-width font-normal">
      这里是有关PSM的介绍。 （在样例模型中，评估使用的函数是 min(100,
      5.7*密码长度))
    </div>
    <div class="pad mar-large shadow border-radius font-normal bac">
      <div class="full-width">
        <div class="mar-large">
          <div class="mar-small">密码：</div>
          <div class="mar-small">
            <el-input
              v-model="password"
              placeholder="请输入需要进行强度评测的密码"
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <el-button
            class="mar-small"
            type="primary"
            @click="submit"
            :loading="isloading"
            >提交</el-button
          >
        </div>

        <div class="mar-large">
          <el-rate
            class="mar-large"
            v-show="showresult"
            v-model="result"
            disabled
            :max="10"
            show-score
            :allow-half="true"
            text-color="#ff9900"
            score-template="{value}"
          >
          </el-rate>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Qs from "qs";
import { Message } from "element-ui";
export default {
  data() {
    return {
      password: null,
      isloading: false,
      showresult: false,
      result: 0,
    };
  },
  methods: {
    toJson: function () {
      return "module:psm,password:" + this.password;
    },
    check: function () {
      var ok =
        !!this.password &&
        this.password.length > 0 &&
        this.password.length < 100;
      if (!ok) {
        Message.error("输入密码不符合要求");
      }
      return ok;
    },
    submit: function () {
      if (this.check()) {
        this.isloading = true;
        this.showresult = false;
        // console.log(this.toJson())
        let payload = {
          msg: this.toJson(),
        };
        axios({
          method: "get",
          params: payload,
          url: "http://localhost:8000/server/server",
        }).then(
            res => {
                this.result = parseFloat(res.data)/10;
                this.showresult = true;
                this.isloading = false;
            }
        )
      }
    },
  },
};
</script>


<style scoped>
.bac {
  background-color: var(--secondary-color-2);
}
.mar-small {
  margin: 8px;
}
.mar-large {
  margin: 20px;
}
.half-width {
  width: 50%;
}
.pad {
  padding: 20px 20px 40px 20px;
}
</style>
