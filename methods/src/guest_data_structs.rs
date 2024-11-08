// Copyright 2024 Diffuse
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! Generated crate containing the image ID and ELF binary of the build guest.

#[derive(serde::Serialize)]
pub struct GuestInputStruct {
    pub json_string: String,
    pub currency_pairs: Vec<String>,
}

pub type GuestInputType = GuestInputStruct;

pub type GuestOutputType = [(String, u64, u64); 4];
