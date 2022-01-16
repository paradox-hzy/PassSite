<template>
  <div>
    <div class="mar-large full-width font-normal">
      这里是有关PassGAN模型的介绍。
    </div>
    <div class="pad mar-large shadow border-radius font-normal bac">
      <el-tabs v-model="type">
        <el-tab-pane label="生成口令" name="gen">
          <div class="full-width">
            <div class="mar-large">
              <div class="mar-small">邮箱：</div>
              <div class="mar-small">
                <el-input
                  v-model="email"
                  placeholder="请输入生成口令发送的目标邮箱"
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <div class="mar-small">生成口令的个数：</div>
              <div class="mar-small">
                <el-input
                  v-model="num"
                  :placeholder="
                    '输入范围' + this.GEN_NUM_MIN + '-' + this.GEN_NUM_MAX
                  "
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <div class="mar-small">生成口令的最小长度值：</div>
              <div class="mar-small">
                <el-input
                  v-model="len"
                  :placeholder="
                    '输入范围' + this.SEQ_MINLEN_MIN + '-' + this.SEQ_MINLEN_MAX
                  "
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <el-button class="mar-small" type="primary" @click="submit"
                >提交</el-button
              >
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="训练模型" name="train">
          <div class="full-width">
            <div class="mar-large">
              <div class="mar-small">邮箱：</div>
              <div class="mar-small">
                <el-input
                  v-model="email"
                  placeholder="请输入生成口令发送的目标邮箱"
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <div class="mar-small">训练迭代次数：</div>
              <div class="mar-small">
                <el-input
                  v-model="iter"
                  :placeholder="
                    '输入范围' + this.ITER_MIN + '-' + this.ITER_MAX
                  "
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <div class="mar-small">生成口令的个数：</div>
              <div class="mar-small">
                <el-input
                  v-model="num"
                  :placeholder="
                    '输入范围' + this.GEN_NUM_MIN + '-' + this.GEN_NUM_MAX
                  "
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <div class="mar-small">生成口令的最小长度值：</div>
              <div class="mar-small">
                <el-input
                  v-model="len"
                  :placeholder="
                    '输入范围' + this.SEQ_MINLEN_MIN + '-' + this.SEQ_MINLEN_MAX
                  "
                ></el-input>
              </div>
            </div>

            <div class="mar-large">
              <el-button class="mar-small" type="primary" @click="submit"
                >提交</el-button
              >
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog title="提示" :visible.sync="dialogVisible" width="30%">
      <span>训练结果稍后会发送至您的邮箱，请不要重复提交！</span>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false"
          >确 定</el-button
        >
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from "axios";
import Qs from "qs";
import {
  ITER_MIN,
  ITER_MAX,
  GEN_NUM_MIN,
  GEN_NUM_MAX,
  SEQ_MINLEN_MIN,
  SEQ_MINLEN_MAX,
} from "../constant/parameters";
import { Message } from "element-ui";
export default {
  data() {
    return {
      ITER_MIN: ITER_MIN,
      ITER_MAX: ITER_MAX,
      GEN_NUM_MIN: GEN_NUM_MIN,
      GEN_NUM_MAX: GEN_NUM_MAX,
      SEQ_MINLEN_MIN: SEQ_MINLEN_MIN,
      SEQ_MINLEN_MAX: SEQ_MINLEN_MAX,
      type: "gen",
      email: null,
      iter: null,
      num: null,
      len: null,
      error: "",
      dialogVisible: false,
    };
  },
  methods: {
    toJson: function () {
      return (
        "module:gan,type:" +
        this.type +
        ",email:" +
        this.email +
        ",iter:" +
        (this.type == "train" ? this.iter : 0) +
        ",num:" +
        this.num +
        ",len:" +
        this.len
      );
    },
    check: function () {
      this.error = "";
      // emial
      const email_re =
        /^([a-zA-Z0-9]+[_|_|\-|.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|_|.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,6}$/;
      if (this.email === null || !email_re.test(this.email)) {
        this.error += "邮箱错误，";
      }
      const digits_re = /\d/;
      // iter
      if (
        this.type === "train" &&
        (!digits_re.test(this.iter) ||
          this.iter < this.ITER_MIN ||
          this.iter > this.ITER_MAX)
      ) {
        this.error += "训练迭代次数错误，";
      }
      // num
      if (
        !digits_re.test(this.num) ||
        this.num < this.GEN_NUM_MIN ||
        this.num > this.GEN_NUM_MAX
      ) {
        this.error += "口令数量错误，";
      }
      // len
      if (
        !digits_re.test(this.len) ||
        this.len < this.SEQ_MINLEN_MIN ||
        this.len > this.SEQ_MINLEN_MAX
      ) {
        this.error += "生成口令长度下限错误，";
      }

      if (this.error !== "") {
        Message.error(this.error);
        return false;
      } else {
        return true;
      }
    },
    submit: function () {
      if (this.check()) {
        this.dialogVisible = true;
        // console.log(this.toJson());
        let payload = {
          msg: this.toJson(),
        }
        axios({
          method: "get",
          params: payload,
          url: "http://localhost:8000/server/server"
        }).then(
          res => {
            console.log("业务编号: "+res.data)
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
